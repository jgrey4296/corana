#!/usr/bin/env python3

import re
from corana.util.parse_data import ParseData
from corana.util.parse_base import ParseBase

import corana.util.xml_utils as XU
from corana.util.utils import guarded_log

import logging as root_logger
logging = root_logger.getLogger(__name__)

def predicate_handler(soup):
    assert(soup.name.lower() == "predicate")
    args = [(x,y) for x,y in soup.attrs.items()]
    data = ParseBase(type="predicate",
                     args=args)
    return data



def rule_handler(soup):
    assert("rule" in soup.name.lower())
    args = [(x,y) for x,y in soup.attrs.items()]
    data = ParseBase(name=soup.name,
                     type="rule",
                     args=args)

    for child in soup.children:
        if isinstance(child, str):
            guarded_log("Skipping rule: {}", child)
            continue
        if "rule" in child.name.lower():
            data.add_component(rule_handler(child))
        else:
            data.add_component(predicate_handler(child))

    return data

def performance_handler(soup):
    assert(soup.name.lower() == "performancerealization")
    args = [(x,y) for x,y in soup.attrs.items()]
    data = ParseBase(type="performance_realization",
                     args=args,
                     name=soup.string)
    return data
