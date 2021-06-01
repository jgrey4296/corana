#!/usr/bin/env python3
import logging as root_logger
from enum import Enum
from os import listdir
from os.path import (abspath, dirname, exists, expanduser, isdir, isfile, join,
                     split, splitext)
from random import shuffle

import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz as pgv
import pyparsing as pp

import code_analysis.util.analysis_case as AC
import code_analysis.util.utils as utils
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_state import ParseState

import parser

LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
single_line_parser = None
multi_line_parser = None


# TODO: classes, functions, imports, components, states, strings, namespaces

# Handle game specific for oxygen, rimworld...
#


def handle_result(pstate, pdata, result):
    return None

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    data  = ParseData(filename)
    state = ParseState()
    while bool(lines):
        state.inc_line()
        # logging.info("line: {}".format(state['line']))
        current = lines.pop(0)

        start_line = state.line
        result = single_line_parser.parseString(current)[0]
        while bool(lines) and not isinstance(result, ParseBase):
            current += lines.pop(0)
            result = multi_line_parser.parseString(current)[0]
            state.inc_line()

        handle_result(state, data, result)
        result.line_no = start_line

    return data



if __name__ == "__main__":
    single_line_parser, multi_line_parser = parser.build_parser()
    input_ext = ".cs"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
