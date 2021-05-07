#!/usr/bin/env python3

from code_analysis.util.parse_data import ParseData

cif_library_components = {'responderinfluenceruleset',
                          'initiatorinfluenceruleset',
                          'performancerealization',
                          'name',
                          'conditionalrules',
                          'conditionrule',
                          'effect',
                          'instantiations',
                          'definition',
                          'instantiation',
                          'rule',
                          'influencerule',
                          'preconditions',
                          'changerule',
                          'toc2',
                          'partialchange',
                          'toc3',
                          'lineofdialogue',
                          'patsyrule',
                          'intents',
                          'effects',
                          'toc1',
                          'microtheory',
                          'chorusrule',
                          'predicate',
                          'socialgame'}

def cif_library_handler(filename, soup):
    data = ParseData(filename)
    data.flag("cif_library")

    contents = soup.find('ciflibraries')
    # flag the SocialGame.name
    data.flag(soup.find("SocialGame")['name'])

    for subgroup_name in ["Intents",
                          "Preconditions",
                          "InitiatorInfluenceRuleSet",
                          "ResponderInfluenceRuleSet",
                          "Effects",
                          "Instantiations"
                          ]:

        subgroup = contents.find(subgroup_name)
        for child in subgroup.children:
            # build
            continue

    # ParseBases:
    ## Rule, conditionrule, influencerule, changerule, chorusrule,
    ## Predicate,
    ## Effect, performancerealization
    ## Instantiation


    data.count(**{x : len(soup.find_all(x)) for x in cif_library_components})

    return data
