#!/usr/bin/env python3
from code_analysis.util.parse_data import ParseData

def promweek_handler(filename, soup):
    data = ParseData(filename)
    contents = soup.find('promweek')
    data['prom_week_contents'] = list({x.name for x in contents if x.name is not None})

    # data = utils.xml_search_components(data, soup, data['prom_week_contents'])
    prom_week_components = {'endings', 'todorule', 'forcedsgs', 'todoitems', 'todolist', 'conditionalrules', 'tidbit', 'quickplayendingdescription', 'cast', 'goalrules', 'description', 'tasknaturallanguage', 'instantiations', 'levels', 'rule', 'goaldescription', 'instantiation', 'todoitem', 'preconditions', 'level', 'toc2', 'partialchange', 'setting', 'forcedsg', 'toc3', 'lineofdialogue', 'condition', 'toc1', 'chorusrule', 'charactername', 'predicate', 'quickplaydescription', 'ending'}
    data['all_counts'] = {x : len(soup.find_all(x)) for x in prom_week_components}

    # TODO todoitem : tidbit, condition, goaldescrptions

    # TODO level : setting, description, goalrules, cast

    # TODO ending : instantiation, preconditions

    return data
