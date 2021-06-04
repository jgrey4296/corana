#!/usr/bin/env python3
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import argparse
from copy import copy
from random import choice, shuffle
import logging as root_logger
from os.path import join, isfile, exists, abspath, dirname
from os.path import split, isdir, splitext, expanduser
from os import listdir, mkdir
import json

logging = root_logger.getLogger(__name__)

from dataclasses import dataclass, field, InitVar
from code_analysis.util.parse_data import ParseData

@dataclass
class AnalysisCase:
    """
    Generalized scaffold for running analysis on code.
    Takes command line arguments :
    -t        : target directories
    -r        : random number of files to analyse
    --randarg : shuffle the files to analyse
    --filter  : filter out already processed files
    -a        : name of the accumulated data file
    """
    DATA_DIR     = "data"
    ANALYSIS_DIR = "analysis"

    curr_file         : str
    exts              : List[str]
    extractor         : Callable
    output_ext        : str           = field(default=".json")
    accumulator       : Callable      = field(default=None)
    finalise          : Callable      = field(default=None)
    accumulated_data  : Dict[Any,Any] = field(default_factory=dict)
    targets           : List[str]     = field(default_factory=list)

    _data_dir         : str       = field(init=False)
    _out_dir          : str       = field(init=False)
    _sources          : List[str] = field(init=False, default_factory=list)
    _files            : List[str] = field(init=False, default_factory=list)
    _args             : Any       = field(init=False, default=None)

    _misc             : Dict[Any,Any] = field(default_factory=dict)

    def __post_init__(self):
        logging.info("Initialising")
        assert(callable(self.extractor))
        assert(self.accumulator is None or callable(self.accumulator))
        assert(self.finalise is None or callable(self.finalise))

        self._data_dir            = join(dirname(self.curr_file), AnalysisCase.DATA_DIR)
        self._out_dir             = join(dirname(self.curr_file), AnalysisCase.ANALYSIS_DIR)

        # Setup specifics:
        self._handle_cli()
        self._setup_sources()
        self._setup_extensions()
        self._get_files()

        # Ensure an output directory:
        if not exists(self._out_dir):
            logging.info("Making {}".format(self._out_dir))
            mkdir(self._out_dir)

    def __call__(self):
        logging.info("Processing")
        # Process each found file:
        for f in self._files:
            # Extract data:
            data = self.extractor(f, self)
            assert(isinstance(data, ParseData))
            if 'discard' in data.flags:
                logging.info(f"Discarding: {data.source_file}")
                continue

            self._accumulate(data)
            # Convert to string
            data_str = data.dumps()
            # Write it out
            self._write_output(f, data_str)

        self._finalise()

        if bool(self.accumulated_data):
            data_str = self._convert_accum_data_to_output_format(self.accumulated_data)
            with open(join("analysis", self._args.accum_name), "w") as f:
                f.write(data_str)

        with open(join(self._out_dir, "analysis_misc.json"),'w') as f:
            json.dump(self._misc, f)


    def _handle_cli(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog = "\n".join([""]))
        parser.add_argument('-o', '--output', default=None)
        parser.add_argument('-t', '--target', action="append", help="Target Dirs and Files")
        parser.add_argument('-a', '--accum_name', default="accumulated_data", help="Name of the accumulated data file")
        parser.add_argument('-r', '--randn', help="Count of random targets to use")
        parser.add_argument('--randarg', action="store_true", help="Shuffle targets")
        parser.add_argument('--filter', action="store_true", help="Filter already processed to prevent duplication")
        self._args = parser.parse_args()

        if self._args.output is not None:
            self._out_dir = abspath(expanduser(self._args.output))

        if self._args.target is not None:
            self.targets += self._args.target

    def _setup_sources(self):
        if bool(self.targets):
            self._sources += self.targets
        else:
            self._sources = [self._data_dir]

    def _setup_extensions(self):
        exts = self.exts
        if isinstance(exts, str):
            exts = [exts]

        self.exts = exts


    def _get_files(self):
        files        = self._dfs_sources()
        subselection = self._subselect_files(files)
        filtered     = self._filter_out_processed(subselection)

        logging.info("Found {} {} files\nUsing {}".format(len(files),
                                                          self.exts,
                                                          len(filtered)))
        if len(filtered) != len(files):
            logging.info("\t{}".format("\n\t".join(filtered)))

        if not bool(filtered):
            raise Exception("No Files to process")

        self._files += filtered


    def _dfs_sources(self):
        """
        DFS the list of sources for files of the correct extension
        """
        logging.info("Getting Data Files")
        ext = self.exts
        initial = self._sources

        files = []
        queue = initial[:]
        logging.info("Searching: {}".format(queue))
        while bool(queue):
            current = queue.pop(0)
            logging.debug("Getting from: {}".format(current))
            if isfile(current) and splitext(current)[1] in ext and current not in files:
                files.append(current)
            elif isdir(current):
                sub = [join(current, x) for x in listdir(current)]
                queue += sub

        return files

    def _subselect_files(self, files):
        # Choose subselection of files if necessary
        if self._args.randn:
            files = [choice(files) for x in range(int(self._args.randn))]

        if self._args.randarg:
            shuffle(files)

        return files

    def _filter_out_processed(self, files):
        #filter already processed
        if self._args.filter:
            filtered_files = []
            for x in files:
                u_path, o_path = self._source_path_to_output_path(x)
                if exists(o_path):
                    continue
                filtered_files.append(x)
                files = filtered_files

        return files


    def _accumulate(self, data):
        if self.accumulator is not None:
            self.accumulated_data = self.accumulator(data,
                                                      self.accumulated_data,
                                                      self)
            assert(isinstance(self.accumulated_data, dict))

    def _finalise(self):
        # Apply final accumulator function
        if self.finalise is not None:
            self.accumulated_data = self.finalise(self.accumulated_data, self)

    def _write_output(self, source_path, data_str):
        u_analysis_path, other = self._source_path_to_output_path(source_path)

        logging.info("Writing output to: {}".format(u_analysis_path))
        with open(u_analysis_path,'w') as f:
            f.write(data_str)



    def _source_path_to_output_path(self, source_path):
        """ a/b/c.txt -> q/y/c_analysis.out """
        ext                  = self.output_ext
        src_name             = splitext(split(source_path)[1])[0]
        header               = split(split(source_path)[0])[1]
        analysis_name        = "{}_{}{}".format(header,src_name, ext)
        orig_analysis_path   = join(self._out_dir,analysis_name)
        unique_analysis_path = orig_analysis_path

        if exists(orig_analysis_path):
            logging.warning("Analysis path already exists: {}".format(orig_analysis_path))
            tmp = list("abcdefg")
            shuffle(tmp)
            analysis_name = "{}_{}_{}{}".format(header,src_name,"".join(tmp), ext)
            unique_analysis_path = join(self._out_dir,analysis_name)

        return unique_analysis_path, orig_analysis_path

    def _convert_accum_data_to_output_format(self, data: Dict[Any, Any]):
        """
        Convert dict to output text.
        Each entry has a line, even lists
        except output_lists,
        which give each item in a list
        """
        logging.info("Converting to output format")
        assert(isinstance(data, dict))
        #expect a dictionary for data
        output_str = ""
        loop_on_keys = self.output_lists

        for k,v in data.items():
            if k in loop_on_keys:
                output_str += "{}:\n".format(str(k))
                for item in v:
                    output_str += "{}\n".format(str(item))

                output_str += "END {}\n".format(str(k))
            else:
                output_str += "{} : {}\n".format(k,str(v))

        return output_str
