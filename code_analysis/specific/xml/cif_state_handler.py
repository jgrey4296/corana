#!/usr/bin/env python3
from code_analysis.util.parse_data import ParseData

def cif_state_handler(filename, soup):
    data = ParseData(filename)
    contents = soup.find('cifstate')
    data['cif_state_contents'] = list({x.name for x in contents if x.name is not None})

    # data = utils.xml_search_components(data, soup, data['cif_state_contents'])
    cif_state_components = {'trait', 'status', 'conditionrule', 'rule', 'relationship', 'character', 'backstorycontext', 'performancerealization', 'edge', 'proposition', 'changerule', 'predicate', 'locution', 'trigger'}
    data['all_counts'] = {x : len(soup.find_all(x)) for x in cif_state_components}

    # TODO sfdb, culturalkd,

    # TODO relationships
    # TODO network edges

    # TODO cast / locutions, traits, statuses


    return data
