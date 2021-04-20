"""
Extract people from a dramatis personae file (ie: Horus Heresy)

output to similarly named files in analysis directory
"""
import spacy
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp
import re

nlp = spacy.load("en_core_web_sm")

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
# Enums and Regexes
BREAK_RE = re.compile('^-+$')

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


def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = {
        'characters' : {}
    }
    lines = []
    group_parser, person_parser = build_parser()
    with open(filename,'r') as f:
        lines = [x.strip() for x in f.readlines()]

    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0,
              'line_after_break' : 0,
              'current_group' : ''}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)

        if current = '':
            continue

        # handle breaks of 20 -'s
        if BREAK_RE.match(current) is not None:
            #new grouping
            state['line_after_break'] = 0
            continue
        else:
            state['line_after_break'] += 1

        if state['line_after_break'] == 1:
            # handle first line after break, setting group
            state['current_group'] = current.strip()

            result = group_parser.parseString(current)
            if result is None:
                continue
            state['current_group'] = result[0]

        else:
            # handle person line
            result = person_parser.parseString(current)
            if result is None:
                continue
            character = result[0]
            if character['name'] not in data['characters']:
                data['characters'][character['name']] = set()
            data['characters'][character['name']].add(state['current_group'])
            data['characters'][character['name']].update(character['data'])

    return data


if __name__ == "__main__":
    input_ext = ".txt"
    output_lists = []
    output_ext = ".narrative_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
