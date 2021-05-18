#!/usr/bin/env python3
import logging as root_logger

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

logging = root_logger.getLogger(__name__)

def build_parser():

    op = pp.Optional
    s = pp.Suppress
    THE = s(pp.CaselessLiteral('The'))
    LEGION = s(pp.CaselessLiteral('Legion') + op(pp.CaselessLiteral('s')))
    ROMAN_N = pp.Word('XIV')
    OF = s(pp.CaselessLiteral('of'))
    ON = s(pp.CaselessLiteral('on'))
    WITH = s(pp.CaselessLiteral('with'))

    BASE_WORD = pp.Word(pp.alphas + '’')

    OPEN_QUOTE = s(pp.Literal('‘'))
    CLOSE_QUOTE = s(pp.Literal('’'))

    NUM = pp.Word(pp.nums)
    NUM_ST = NUM + pp.Or([pp.CaselessLiteral('st'),
                          pp.CaselessLiteral('nd'),
                          pp.CaselessLiteral('rd'),
                          pp.CaselessLiteral('th')])

    op_quote_name = pp.Optional(OPEN_QUOTE + pp.OneOrMore(BASE_WORD) + CLOSE_QUOTE)

    # Group parsers:
    legion_p = THE + ROMAN_N + LEGION + op_quote_name
    legion_p2 = THE + pp.OneOrMore(BASE_WORD) + LEGION

    the_fleet = THE + NUM_ST + pp.OneOrMore(BASE_WORD)
    with_fleet = WITH + THE + pp.OneOrMore(BASE_WORD) + NUM_ST + pp.OneOrMore(BASE_WORD)

    the_x_of_y = THE + pp.OneOrMore(BASE_WORD) + OF + pp.OneOrMore(BASE_WORD)
    the_x_p = op(pp.OneOrMore(pp.Or([THE, ON, WITH]))) + pp.OneOrMore(BASE_WORD)

    group_parser = pp.MatchFirst([legion_p, legion_p2,
                                  the_fleet,
                                  with_fleet,
                                  the_x_of_y,
                                  the_x_p])

    # Person Parsers:
    comma = pp.Literal(',')
    NAME = pp.OneOrMore(BASE_WORD)
    HONORIFIC = None
    COMPANY = None
    RANK = None
    AND = None
    X_of_Y = None
    PRIMARCH = None

    person_parser = NAME + op(s(comma) + pp.commaSeparatedList)
    # TODO parse out names and components
    # TODO  name , [titles]
    # TODO  handle monikers / Called X / also known as X
    # TODO  handle ranks
    # TODO  handle company's
    # TODO  handle X to|of the? Y
    # TODO  handle X's Y



    return group_parser, person_parser
