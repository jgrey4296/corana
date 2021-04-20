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

import analysis_case as AC
import utils

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

class LuaClass(utils.ParseBase):

    def __init__(self, name, parent=None):
        super().__init__()
        self._type = "Class"
        self._name = name
        self._parent = parent

    def __str__(self):
        parent = ""
        if self._parent is not None:
            parent = self._parent

        return "{} : {} : {} : {}".format(self._line_no,
                                          self._type,
                                          self._name,
                                          self._parent)

class LuaFn(utils.ParseBase):

    def __init__(self, name):
        super().__init__()
        self._type = "Function"
        self._name = name

class LuaRecipe(utils.ParseBase):

    def __init__(self, name, rest):
        super().__init__()
        self._type = "Recipe"
        self._name = name
        self._rest = rest

    def __str__(self):
        return "{} : {} : {} : {}".format(self._line_no,
                                          self._type,
                                          self._name,
                                          self._rest)



def build_parser():

    # Parse Utilities
    s = pp.Suppress
    op = pp.Optional
    lineEnd = pp.lineEnd
    NAME = pp.Word(pp.alphanums + ":_.")
    NUM = pp.Word(pp.nums + ".")
    EQUAL = s(pp.Literal('='))
    COLON = pp.Literal(':')
    FN = s(pp.Keyword("function"))
    CLS = s(pp.Keyword('Class'))
    END = s(pp.Keyword('end'))
    SELF = pp.Keyword('self')
    LOCAL = pp.Keyword("local")
    OPAR = s(pp.Literal('('))
    CPAR = s(pp.Literal(')'))
    RECIPE = s(pp.Keyword('Recipe'))
    COMMA = s(pp.Literal(','))


    class_p = NAME.setResultsName('name') + EQUAL + CLS + OPAR + pp.Or([FN, NAME.setResultsName('parent')])
    function_p = op(LOCAL) + FN + NAME.setResultsName('name')
    recipe_p = RECIPE + OPAR + pp.quotedString.setResultsName('name') \
        + COMMA + pp.restOfLine.setResultsName('rest')

    #addTask
    #states, events

    #TODO:Setup parse results
    class_p.setParseAction(lambda x: LuaClass(x.name, x.parent))
    function_p.setParseAction(lambda x: LuaFn(x.name))
    recipe_p.setParseAction(lambda x: LuaRecipe(x.name, x.rest))

    com_open = pp.Literal('--')
    com_parser = s(com_open) + pp.restOfLine
    com_parser.setParseAction(lambda x: lua_e.COMMENT)

    main_parser = pp.MatchFirst([com_parser,
                                 class_p,
                                 function_p,
                                 recipe_p,
                                 pp.restOfLine])
    return main_parser

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
    output_lists = ["classes", "functions","recipes"]
    output_ext = ".lua_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
