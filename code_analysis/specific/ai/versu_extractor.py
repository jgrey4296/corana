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

from dataclasses import asdict

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

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

from versu_struct import versu_e, Enum_to_String, VersuBlock, VersuExpression
from versu_parser import build_parser

Quote_Extractor = pp.ZeroOrMore(pp.Suppress(pp.SkipTo(pp.quotedString)) + pp.quotedString)


#----------------------------------------

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    main_parser = build_parser()
    #Data to return:
    parse_data = ParseData(filename)
    #Intermediate parsing state
    parse_state = ParseState()

    #Read the file:
    lines = []
    with open(filename,'rb') as f:
        lines = [x.decode('utf-8','ignore') for x in f.readlines()]


    #Parse:
    while bool(lines):
        parse_state.inc_line()
        # TODO strip comments
        # TODO construct trie
        # logging.info("Line: {}".format(parse_state['line']))
        current = lines.pop(0).strip()

        #Handle simple syntax cues
        if current == "":
            continue
        if parse_state.fold_into_last:
            current = parse_state.last_line + current
            parse_state.fold_into_last = False

        if current == "{":
            parse_state.in_def = True
            parse_state.def_prefix = parse_state.last_line
            continue
        elif current == "}":
            parse_state.in_def = None
            continue

        if parse_state.in_def and parse_state.def_prefix:
            current = "{}.{}".format(parse_state.def_prefix, current)

        #PARSE
        result = main_parser.parseString(current)[0]

        if isinstance(result, ParseBase):
            result.line_no = parse_state.line

        #Handle Blocks:
        if result is versu_e.COPEN: #comment
            parse_data.inc_comment()
            parse_state.in_block.append(versu_e.COMMENT)
            continue
        elif result is versu_e.CCLOSE: #comment close
            parse_data.inc_comment()
            # TODO ensure you pop a comment
            parse_state.in_block.pop()
            continue
        elif bool(parse_state.in_block) and parse_state.in_block[-1] is versu_e.COMMENT or result is versu_e.COMMENT:
            parse_data.inc_comment()
            continue
        elif current[-1] == "." or current[-1] == "!":
            parse_state.last_line = current
            parse_state.fold_into_last = True
            continue
        elif isinstance(result, VersuBlock):
            parse_state.in_block.append(result)

            parse_data.insert(result, "block")
            if result.type == "function":
                parse_data.insert(result, "function")

        elif result is versu_e.END: #block end
            ending = parse_state.in_block
            if bool(parse_state.in_block):
                parse_state.in_block.pop()
            #TODO COPY and END
            end_exp = VersuExpression('end','')
            end_exp.line_no = parse_state.line
            parse_data.insert(end_exp)

        #Handle Expressions:
        elif isinstance(result, VersuExpression):
            #TODO: Add block height
            if bool(parse_state.in_block) and isinstance(parse_state.in_block[-1], VersuBlock) and parse_state.in_block[-1].type == "types":
                parse_data.insert(result, "type")
            else:
                parse_data.insert(result, result.type)


        #Handle other simple syntax based counts:
        parse_data.count(non_exclusion=current.count("."),
                         exclusion=current.count("!"))

        potential_strings = Quote_Extractor.parseString(current)
        parse_data.strings += potential_strings[:]


        parse_state.last_line = current

    # TODO Export into trie-explorer usable format

    return parse_data


if __name__ == "__main__":
    input_ext    = [".type", ".data", ".praxis"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
