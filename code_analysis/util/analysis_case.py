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

logging = root_logger.getLogger(__name__)


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
    DATA_DIR = "data"
    ANALYSIS_DIR = "analysis"

    def __init__(self,
                 curr_file         : str,
                 exts              : List[str],
                 extractor         : Callable,
                 output_lists      : List[str],
                 output_ext        : str,
                 accumulator       : Callable=None,
                 accumulator_final : Callable=None,
                 init_accum        : Any=None,
                 targets           : List[str]=None):
        """
        sources           : list of sources to process (+ cli targets)
        exts              : list of extensions to process
        extractor         : extractor function called on a file
        output_lists      : keys of return data to treat as lists, not as dicts
        output_ext        : the extension of the processed output
        accumulator       : function called on processed data and the accumulator data
        accumulator_final : function called on the final accumulator data
        init_accum        : start value for accumulator
        """
        logging.info("Initialising")
        assert(callable(extractor))
        assert(accumulator is None or callable(accumulator))
        assert(accumulator_final is None or callable(accumulator_final))

        self._curr_file           = curr_file
        self._data_dir            = join(dirname(curr_file), AnalysisCase.DATA_DIR)
        self._out_dir             = join(dirname(curr_file), AnalysisCase.ANALYSIS_DIR)
        self._sources             = []
        self._extensions          = []
        self._output_lists        = []
        self._files               = []
        self._output_extension    = output_ext
        self._extractor           = extractor
        self._accumulator         = accumulator
        self._accumulator_final   = accumulator_final
        self._accumulator_initial = init_accum

        self._accumulated_data = None

        # Setup specifics:
        self._handle_cli()
        self._setup_sources(targets)
        self._setup_extensions(exts)
        self._setup_output_lists(output_lists)
        self._get_files()

        # Ensure an output directory:
        if not exists(self._out_dir):
            logging.info("Making {}".format(self._out_dir))
            mkdir(self._out_dir)

    def __call__(self):
        logging.info("Processing")
        self._accumulated_data = copy(self._accumulator_initial)
        # Process each found file:
        for f in self._files:
            # Extract data:
            data = self._extractor(f, self)
            self._accumulate(data)
            # Convert to string
            data_str = self._convert_data_to_output_format(data)
            # Write it out
            self._write_output(f, data_str)

        self._finalise()

        if bool(self._accumulated_data):
            data_str = self._convert_data_to_output_format(self._accumulated_data)
            with open(join("analysis", self.args.accum_name), "w") as f:
                f.write(data_str)



    def _handle_cli(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog = "\n".join([""]))
        parser.add_argument('-o', '--output', default=None)
        parser.add_argument('-t', '--target', action="append", help="Target Dirs and Files")
        parser.add_argument('-a', '--accum_name', default="accumulated_data", help="Name of the accumulated data file")
        parser.add_argument('-r', '--randn', help="Count of random targets to use")
        parser.add_argument('--randarg', action="store_true", help="Shuffle targets")
        parser.add_argument('--filter', action="store_true", help="Filter already processed to prevent duplication")
        self.args = parser.parse_args()

        if self.args.output is not None:
            self._out_dir = abspath(expanduser(self.args.output))

        if self.args.target is not None:
            self._sources += self.args.target

    def _setup_sources(self, targets):
        if targets is not None:
            self._sources += targets
        else:
            self._sources = [self._data_dir]

    def _setup_extensions(self, exts):
        if isinstance(exts, list) and not isinstance(exts, str):
            self._extensions += exts
        else:
            self._extensions.append(exts)

    def _setup_output_lists(self, output_lists):
        if output_lists is not None and not isinstance(output_lists, str):
            self._output_lists += output_lists
        elif output_lists is not None:
            self._output_lists.append(output_lists)

    def _get_files(self):
        files        = self._dfs_sources()
        subselection = self._subselect_files(files)
        filtered     = self._filter_out_processed(subselection)

        logging.info("Found {} {} files\nUsing {}".format(len(files),
                                                          self._extensions,
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
        ext = self._extensions
        initial = self._sources

        files = []
        queue = initial[:]
        while bool(queue):
            current = queue.pop(0)
            logging.debug("Getting from: {}".format(current))
            if isfile(current) and splitext(current)[1] in ext:
                files.append(current)
            elif isdir(current):
                sub = [join(current,x) for x in listdir(current)]
                queue += sub

        return files

    def _subselect_files(self, files):
        # Choose subselection of files if necessary
        if self.args.randn:
            files = [choice(files) for x in range(int(self.args.randn))]

        if self.args.randarg:
            shuffle(files)

        return files

    def _filter_out_processed(self, files):
        #filter already processed
        if self.args.filter:
            filtered_files = []
            for x in files:
                u_path, o_path = self._source_path_to_output_path(x)
                if exists(o_path):
                    continue
                filtered_files.append(x)
                files = filtered_files

        return files


    def _accumulate(self, data):
        if self._accumulator is not None:
            self._accumulated_data = self._accumulator(data, self._accumulated_data, self)

    def _finalise(self):
        # Apply final accumulator function
        if self._accumulator_final is not None:
            self._accumulated_data = self._accumulator_final(self._accumulated_data, self)

    def _write_output(self, source_path, data_str):
        u_analysis_path, other = self._source_path_to_output_path(source_path)

        logging.info("Writing output to: {}".format(u_analysis_path))
        with open(u_analysis_path,'w') as f:
            f.write(data_str)



    def _source_path_to_output_path(self, source_path):
        """ a/b/c.txt -> q/y/c_analysis.out """
        ext                  = self._output_extension
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
            unique_analysis_path = join("analysis",analysis_name)

        return unique_analysis_path, orig_analysis_path



    def _convert_data_to_output_format(self, data: Dict[Any, Any]):
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
        loop_on_keys = self._output_lists

        for k,v in data.items():
            if k in loop_on_keys:
                for item in v:
                    output_str += "{}\n".format(str(item))
            else:
                output_str += "{} : {}\n".format(k,str(v))

        return output_str