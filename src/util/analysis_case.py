#!/usr/bin/env python3
import argparse
from copy import copy
from random import choice, shuffle
import logging as root_logger
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir

logging = root_logger.getLogger(__name__)


class AnalysisCase:

    def __init__(self, sources, exts, extractor,
                 output_lists, output_ext,
                 accumulator=None, accumulator_final=None,
                 init_accum=None):
        logging.info("Initialising")
        assert(callable(extractor))
        assert(accumulator is None or callable(accumulator))
        assert(accumulator_final is None or callable(accumulator_final))

        parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                         epilog = "\n".join([""]))
        parser.add_argument('-t', '--target', action="append")
        parser.add_argument('-r', '--randn')
        parser.add_argument('--randarg', action="store_true")
        parser.add_argument('--filter', action="store_true")
        parser.add_argument('-a', '--accum_name', default="accumulated_data")
        self.args = parser.parse_args()

        self._sources = []
        self._extensions = []
        self._output_lists = []
        self._output_extension = output_ext
        self._extractor = extractor
        self._accumulator = accumulator
        self._accumulator_final = accumulator_final
        self._accumulator_initial = init_accum

        self._accumulated_data = None

        if isinstance(exts, list) and not isinstance(exts, str):
            self._extensions += exts
        else:
            self._extensions.append(exts)

        if self.args.target is not None:
            self._sources += self.args.target
        elif isinstance(sources, str):
            self._sources.append(sources)
        else:
            self._sources += sources

        if output_lists is not None and not isinstance(output_lists, str):
            self._output_lists += output_lists
        elif output_lists is not None:
            self._output_lists.append(output_lists)

        # Get the files ready
        files = self.get_files()
        subselection = self.subselect_files(files)
        filtered = self.filter_out_processed(subselection)

        logging.info("Found {} {} files\nUsing {}".format(len(files),
                                                          self._extensions,
                                                          len(filtered)))
        if len(filtered) != len(files):
            logging.info("\t{}".format("\n\t".join(filtered)))
        self._files = filtered

    def get_files(self):
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

    def subselect_files(self, files):
        # Choose subselection of files if necessary
        if self.args.randn:
            files = [choice(files) for x in range(int(self.args.randn))]

        if self.args.randarg:
            shuffle(files)

        return files

    def filter_out_processed(self, files):
        #filter already processed
        if self.args.filter:
            filtered_files = []
            for x in files:
                u_path, o_path = self.source_path_to_output_path(x)
                if exists(o_path):
                    continue
                filtered_files.append(x)
                files = filtered_files

        return files

    def __call__(self):
        logging.info("Processing")
        self._accumulated_data = copy(self._accumulator_initial)
        # Process each found file:
        for f in self._files:
            # Extract data:
            data = self._extractor(f)
            self.accumulate(data)
            # Convert to string
            data_str = self.convert_data_to_output_format(data)
            # Write it out
            self.write_output(f, data_str)

        self.finalise()

        if bool(self._accumulated_data):
            data_str = self.convert_data_to_output_format(self._accumulated_data)
            with open(join("analysis", self.args.accum_name), "w") as f:
                f.write(data_str)


    def accumulate(self, data):
        if self._accumulator is not None:
            self._accumulated_data = self._accumulator(data, self._accumulated_data)

    def finalise(self):
        # Apply final accumulator function
        if self._accumulator_final is not None:
            self._accumulated_data = self._accumulator_final(self._accumulated_data)

    def write_output(self, source_path, data_str):
        u_analysis_path, other = self.source_path_to_output_path(source_path)

        logging.info("Writing output to: {}".format(u_analysis_path))
        with open(u_analysis_path,'w') as f:
            f.write(data_str)



    def source_path_to_output_path(self, source_path):
        ext = self._output_extension
        src_name = splitext(split(source_path)[1])[0]
        header = split(split(source_path)[0])[1]
        analysis_name = "{}_{}{}".format(header,src_name, ext)
        orig_analysis_path = join("analysis",analysis_name)
        unique_analysis_path = orig_analysis_path

        if exists(orig_analysis_path):
            logging.warning("Analysis path already exists: {}".format(orig_analysis_path))
            tmp = list("abcdefg")
            shuffle(tmp)
            analysis_name = "{}_{}_{}{}".format(header,src_name,"".join(tmp), ext)
            unique_analysis_path = join("analysis",analysis_name)

        return unique_analysis_path, orig_analysis_path



    def convert_data_to_output_format(self, data):
        """
        Convert dict to output text.
        Each entry has a line, even lists
        except output_lists,
        which give each item in a list
        """
        logging.info("Converting to output format")
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
