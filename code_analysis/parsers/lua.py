#!/usr/bin/env python3
import pyparsing as pp
from pyparsing import pyparsing_common as ppc

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
