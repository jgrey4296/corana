#!/usr/bin/env python3

from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir, mkdir

import json

#https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field, InitVar

@dataclass
class PostProcessor:
    """
    Read analysis files and produce aggregate information,
    create diagrams, etc
    """

    root        : str      = field()
    processor   : Callable = field()
    accumulator : Callable = field(default=None)
    finalise    : Callable = field(default=None)

    _analysis_dir : str = field(init=False)
    _out_dir      : str = field(init=False)
    _accumulate_data : Dict[Any,Any] = field(init=False, default_factory=dict)

    _files        : List[str] = field(init=False)

    def __post_init__(self, other):
        self._analysis_dir = join(dirname(self.root), "analysis")
        self._out_dir      = join(dirname(self.root), "post_analysis")

        if not exists(self._analysis_dir):
            raise Exception("Analysis Directory doesn't exist: {}".format(self._analysis_dir))

        # if outdir doesn't exist, create it
        if not exists(self._out_dir):
            mkdir(self._out_dir)

        self._get_files()

    def __call__(self):
        # find files
        data = None
        for f in self._files:
            with open(f) as f_in:
                data = json.load(f)
            assert(data is not None)
            logging.info("Loaded {}".format(f))
            # TODO reconstruct parse objects

            # process
            result = self.processor(data)

            self._output(result)
            self._accumulate(result)

        self._finalise()
        if bool(self.accumulate_data):
            self._output(self.accumulate_data)


    def _output(self, data):
        raise NotImplementedError()


    def _handle_cli(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog = "\n".join([""]))
        parser.add_argument('-a', '--accum_name', default="accumulated_data", help="Name of the accumulated data file")
        parser.add_argument('-r', '--randn', help="Count of random targets to use")
        parser.add_argument('--randarg', action="store_true", help="Shuffle targets")
        parser.add_argument('--filter', action="store_true", help="Filter already processed to prevent duplication")
        self._args = parser.parse_args()

    def _get_files(self):
        files        = [join(self._analysis_dir, x) for x in listdir(self._analysis_dir) if splitext(x)[1] == ".json"]
        filtered     = self._filter_out_processed(subselection)

        logging.info("Found {} files\nUsing {}".format(len(files),
                                                       len(filtered)))
        if len(filtered) != len(files):
            logging.info("\t{}".format("\n\t".join(filtered)))

        if not bool(filtered):
            raise Exception("No Files to process")

        self._files += filtered


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



    def _source_path_to_output_path(self, source_path):
        """ a/b/c.json-> q/y/post_c.json"""
        ext                  = ".json"
        src_name             = splitext(split(source_path)[1])[0]
        post_analysis_name   = "post_{}{}".format(src_name, ext)
        orig_analysis_path   = join(self._out_dir,post_analysis_name)
        unique_analysis_path = orig_analysis_path

        if exists(orig_analysis_path):
            logging.warning("Analysis path already exists: {}".format(orig_analysis_path))
            tmp = list("abcdefg")
            shuffle(tmp)
            post_analysis_name = "post_{}_{}{}".format(src_name,
                                                       "".join(tmp),
                                                       ext)
            unique_analysis_path = join(self._out_dir,
                                        post_analysis_name)

        return unique_analysis_path, orig_analysis_path

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
