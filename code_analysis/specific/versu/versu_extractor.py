"""
Get versu files from data dir,

output to similarly named files in analysis directory
"""
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase

# Setup root_logger:
from os.path import splitext, split
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################

from versu_struct import versu_e, Enum_to_String, TempData, ParseState
from versu_parser import build_parser

Quote_Extractor = pp.ZeroOrMore(pp.Suppress(pp.SkipTo(pp.quotedString)) + pp.quotedString)


#----------------------------------------

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    main_parser = build_parser()
    #Data to return:
    data = TempData()

    #Read the file:
    lines = []
    with open(filename,'rb') as f:
        lines = [x.decode('utf-8','ignore') for x in f.readlines()]

    #Intermediate parsing state:
    state = ParseState()
    #Parse:
    while bool(lines):
        state['line'] += 1
        # TODO strip comments
        # TODO construct trie
        # logging.info("Line: {}".format(state['line']))
        current = lines.pop(0).strip()

        #Handle simple syntax cues
        if current == "":
            continue
        if state.fold_into_last:
            current = state.last_line + current
            state.fold_into_last = False
        if current == "{":
            state.in_def = True
            statedef_prefix = state['last_line']
            continue
        elif current == "}":
            state.in_def = None
            continue

        if state.in_def and statedef_prefix:
            current = "{}.{}".format(state.def_prefix,current)

        #PARSE
        result = main_parser.parseString(current)[0]

        if isinstance(result, ParseBase):
            result.line_no = state.line

        #Handle Blocks:
        if result is versu_e.COPEN: #comment
            data.comments += 1
            state.in_block.append(versu_e.COMMENT)
            continue
        elif result is versu_e.CCLOSE: #comment close
            data.comments += 1
            state.in_block.pop()
            continue
        elif bool(state.in_block) and state.in_block[-1] is versu_e.COMMENT or result is versu_e.COMMENT:
            data.comments += 1
            continue
        elif current[-1] == "." or current[-1] == "!":
            state.last_line = current
            state.fold_into_last = True
            continue

        elif isinstance(result, VersuBlock):
            state.in_block.append(result)
            data.in_order.append(result)
            data.blocks.append(result)
            if result.type == "function":
                data.functions.append(result)

        elif result is versu_e.END: #block end
            ending = state.in_block
            if bool(state.in_block):
                state.in_block.pop()
            #TODO COPY and END
            end_exp = VersuExpression('end','')
            end_exp.line_no = state['line']
            data.in_order.append(end_exp)

        #Handle Expressions:
        elif isinstance(result, VersuExpression):
            #TODO: Add block height
            data.in_order.append(result)
            if result.type == 'insert':
                data.inserts.append(result)
            elif result.type == "action":
                data.actions.append(result)
            elif bool(state.in_block) and isinstance(state.in_block[-1], VersuBlock) and state.in_block[-1].type == "types":
                data.types.append(result)


        #Handle other simple syntax based counts:
        data.non_exclusions += current.count('.')
        data.exclusions += current.count('!')

        potential_strings = Quote_Extractor.parseString(current)
        data.strings += potential_strings[:]


        state.last_line = current

    # TODO Export into trie-explorer usable format


    data.in_order.sort()
    return data


if __name__ == "__main__":
    input_ext    = [".type", ".data", ".praxis"]
    output_lists = ['in_order']
    output_ext   = ".versu_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
