#!/usr/bin/env python3
from code_analysis.util.parse_data import ParseData

def promweek_handler(filename, soup):
    data = ParseData(filename)
    contents = soup.find('promweek')

    # TODO todoitem : tidbit, condition, goaldescrptions

    # TODO level : setting, description, goalrules, cast

    # TODO ending : instantiation, preconditions

    return data
