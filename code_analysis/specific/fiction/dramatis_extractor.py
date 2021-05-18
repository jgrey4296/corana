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
# Enums and Regexes
BREAK_RE = re.compile('^-+$')


def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData(filename)

    lines = []
    group_parser, person_parser = build_parser()
    with open(filename,'r') as f:
        lines = [x.strip() for x in f.readlines()]

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0,
    #           'line_after_break' : 0,
    #           'current_group' : ''}
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

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)
