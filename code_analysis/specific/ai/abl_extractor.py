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

import json
import abl_struct as ABS
import abl_parser as ABP
import code_analysis.util.analysis_case as AC
import code_analysis.util.utils as utils
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_state import ParseState

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

single_line_parser = None
multi_line_parser = None

def handle_result(pstate, pdata, presult):
    logging.debug(f"Handling Result: {presult}")
    try:
        if presult is obj_e.COMMENT:
            pdata.inc_comment()
            return

        assert(json.dumps(presult.to_dict()))
        if isinstance(presult, ABS.AblEnt):
            pdata.insert(presult, "behaving_entity")
        elif isinstance(presult, ABS.AblRegistration):
            pdata.insert(presult, "registration")
        elif isinstance(presult, ABS.AblBehavior):
            pdata.insert(presult, "behaviour")
            pstate.current = presult
        elif isinstance(presult, ABS.AblComponent):
            pstate.current.add_component(presult)
            pdata.insert(presult)
        elif isinstance(presult, ABS.AblMisc):
            pdata.insert(presult)
        elif isinstance(presult, ParseBase):
            arg_empty = all([x in ["", "}"] for x in presult.args])
            if presult.name == "Pass" and arg_empty:
                return
            pdata.insert(presult)
        else:
            logging.warning("Unrecognised parse result: {}".format(presult))

    except AttributeError as err:
        logging.warning(str(err))
        breakpoint()
        logging.info("Error")


def extract_from_file(filename, ctx):
    logging.info(f"Extracting from: {filename}")
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    data  = ParseData(filename)
    state = ParseState()
    while bool(lines):
        state.inc_line()
        # logging.info("line: {}".format(state['line']))
        current = lines.pop(0).strip()
        if not bool(current):
            continue

        start_line = state.line
        try:
            result = single_line_parser.parseString(current)[0]
            if not isinstance(result, ParseBase):
                logging.debug("Shifting to multi line parser")
            while not isinstance(result, ParseBase) and bool(lines) :
                current += lines.pop(0).strip()
                result = multi_line_parser.parseString(current)[0]
                state.inc_line()

            result.line_no = start_line
            handle_result(state, data, result)
        except Exception as err:
            breakpoint()
            logging.info("Error: {}".format(err))


    return data


if __name__ == "__main__":
    single_line_parser, multi_line_parser = ABP.build_parser()
    input_ext = ".abl"


    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
