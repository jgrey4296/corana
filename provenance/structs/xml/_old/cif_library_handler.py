#!/usr/bin/env python3

import re
from provenance.util.parse_data import ParseData
from provenance.util.parse_base import ParseBase

import provenance.util.xml_utils as XU

from cif_shared_handlers import predicate_handler, rule_handler, performance_handler

import logging as root_logger
logging = root_logger.getLogger(__name__)


RULE_RE = re.compile("rule")
TOC_RE  = re.compile("toc[0-9]")

def cif_library_handler(filename, soup):
    data = ParseData(filename)
    data.flag("cif_library")

    assert(soup.ciflibraries)

    social_games = soup.ciflibraries.socialgamelibrary.find_all("socialgame",
                                                                recursive=False)

    for social_game in social_games:
        game_name = social_game['name']
        data.flag(game_name)

        data.insert(rule_wrap_handler(social_game.patsyrule), game_name)
        data.insert(rule_wrap_handler(social_game.intents), game_name)
        data.insert(rule_wrap_handler(social_game.preconditions), game_name)
        data.insert(rule_wrap_handler(social_game.initiatorinfluenceruleset), game_name)
        data.insert(rule_wrap_handler(social_game.responderinfluenceruleset), game_name)

        effects = social_game.effects
        for effect in effects.children:
            if isinstance(effect, str):
                continue
            data.insert(effect_handler(effect), game_name)

        instantiations = social_game.instantiations
        for instantiation in instantiations.children:
            if isinstance(instantiation, str):
                continue
            data.insert(instantiation_handler(instantiation), game_name)

    microtheories = soup.microtheories
    if microtheories:
        for microtheory in microtheories.children:
            if isinstance(microtheory, str):
                continue
            data.insert(micro_handler(microtheory), "microtheories")

    return data




def effect_handler(soup):
    assert(soup.name.lower() == "effect")
    args = [(x,y) for x,y in soup.attrs.items()]
    data = ParseBase(type="effect",
                     args=args)

    XU.verify_schema(soup,["PerformanceRealization", "ConditionRule", "ChangeRule"])
    # handle performance realization
    data.add_component(performance_handler(soup.performancerealization))
    # handle condition rule
    data.add_component(rule_handler(soup.conditionrule))
    # handle change rule
    data.add_component(rule_handler(soup.changerule))

    return data


def instantiation_handler(soup):
    assert(soup.name.lower() == "instantiation")
    args = [(x,y) for x,y in soup.attrs.items() if x not in ['name']]
    name = "Anon Instantiation"
    if "name" in soup.attrs:
        name = soup['name']

    data = ParseBase(name=name,
                     type="instantiation",
                     args=args)

    XU.verify_schema(soup, ["lineofdialogue",
                            "toc1",
                            "toc2",
                            "toc3",
                            "conditionalrules"])

    lines = soup.find_all("lineofdialogue", recursive=False)
    tocs = soup.find_all(TOC_RE, recursive=False)
    cond_rules = soup.conditionalrules

    data.add_component(None, as_list=[dialogue_handler(x) for x in lines])
    data.add_component(None, as_list=[toc_handler(x) for x in tocs])
    data.add_component(rule_wrap_handler(cond_rules))

    return data

def dialogue_handler(soup):
    assert(soup.name.lower() == "lineofdialogue")
    args = [(x,y) for x,y in soup.attrs.items()]
    data = ParseBase(type="line_of_dialogue",
                     args=args)

    data.add_component(None, as_list=[rule_wrap_handler(x) for x in soup.children])

    return data

def rule_wrap_handler(soup):
    if soup is None or soup == "\n":
        return None

    args = [(x,y) for x,y in soup.attrs.items()]
    data = ParseBase(name=soup.name,
                     args=args,
                     type="rule wrapper")

    rules = soup.find_all(RULE_RE, recursive=False)

    data.add_component(None, as_list=[rule_handler(x) for x in rules])
    return data



def toc_handler(soup):
    assert("toc" in soup.name.lower())
    args = {"id" : soup.name}
    data = ParseBase(type="ToC",
                     args=args,
                     name=soup.string
                     )
    return data


def micro_handler(soup):
    assert(soup.name.lower() == "microtheory")
    XU.verify_schema(soup, ["name", "definition", "initiatorinfluenceruleset", "responderinfluenceruleset"])
    data = ParseBase(name=soup.find("name").string,
                     type="microtheory")

    other_than_name = [rule_wrap_handler(x) for x in soup.children
                       if x.name != "name"]
    data.add_component(None, as_list=other_than_name)

    return data
