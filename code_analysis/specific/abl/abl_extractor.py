"""
Get abl files from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
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

import abl_struct as ABS
import abl_parser as ABP
import code_analysis.util.analysis_case as AC
import code_analysis.util.utils as utils
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_base import ParseBase

LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
# Enums:
obj_e = ABS.ABL_E

main_parser = None

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData()
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    state = {'bracket_count' : 0,
             'current' : None,
             'line' : 0}

    while bool(lines):
        state['line'] += 1
        # logging.info("line: {}".format(state['line']))
        current = lines.pop(0)

        result = main_parser.parseString(current)[0]
        if not result:
            continue

        if isinstance(result, ParseBase):
            result.line_no = state['line']

        try:
            if result is obj_e.COMMENT:
                data.inc_comment()
            elif isinstance(result, ABS.AblEnt):
                data.insert(result, "behaving_entity")
            elif isinstance(result, ABS.AblRegistration):
                data.insert(result, "registration")
            elif isinstance(result, ABS.AblBehavior):
                data.insert(result, "behaviour")
                state['current'] = result
            elif isinstance(result, ABS.AblComponent):
                state['current'].add_component(result)
            elif not isinstance(result, ParseBase):
                logging.warning("Unrecognised parse result: {}".format(result))

        except AttributeError as err:
            breakpoint()
            logging.info("Error")

    return data


if __name__ == "__main__":
    main_parser = ABP.build_parser()
    input_ext = ".abl"
    output_ext = ".abl_analysis"


    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_ext)()
