"""
Get lua files from data dir,

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
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

# Setup root_logger:
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
lua_e = Enum('Lua Enums','COMMENT')


def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    main_parser = build_parser()
    data = { 'comments' : 0,
             'classes' : [],
             'functions' : [],
             'recipes' : [],
             'state' : [],
             'events' : []
             }
    lines = []
    with open(filename,'rb') as f:
        lines = [x.decode('utf-8','ignore') for x in f.readlines()]

    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)

        result = main_parser.parseString(current)[0]

        if isinstance(result, utils.ParseBase):
            result._line_no = state['line']

        if isinstance(result, lua_e) and result is lua_e.COMMENT:
            data['comments'] += 1
        elif isinstance(result, LuaClass):
            data['classes'].append(result)
        elif isinstance(result, LuaFn):
            data['functions'].append(result)
        elif isinstance(result, LuaRecipe):
            data['recipes'].append(result)


    return data


if __name__ == "__main__":
    input_ext = ".lua"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
