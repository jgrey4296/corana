#!/usr/bin/env python3
import logging as root_logger
import re

import corana.util.xml_utils as XU
from corana.util.parse_base import ParseBase
from corana.util.parse_data import ParseData
from corana.util.utils import guarded_log

import cif_shared_handlers as CSH

logging = root_logger.getLogger(__name__)


def cif_state_handler(filename, soup):
    data = ParseData(filename)
    contents = soup.find('cifstate')

    data.insert(container_handler(contents.triggers))
    data.insert(container_handler(contents.network))
    data.insert(container_handler(contents.relationships))
    data.insert(container_handler(contents.cast))
    data.insert(container_handler(contents.culturalkb))
    data.insert(container_handler(contents.sfdb))

    return data


def container_handler(soup):
    if soup is None:
        return None

    data = ParseBase(type="container",
                     name=soup.name.lower(),
                     args=[(x,y) for x,y in soup.attrs.items()])

    lookup = {"trigger"          : trigger_handler,
              "edge"             : simple_tag_handler,
              "relationship"     : simple_tag_handler,
              "character"        : character_handler,
              "proposition"      : simple_tag_handler,
              "backstorycontext" : simple_tag_handler}

    for child in soup.children:
        if isinstance(child, str):
            guarded_log("Skipping container: {}", child)
            continue

        data.add_component(lookup[child.name](child))

    return data

def trigger_handler(soup):
    data = ParseBase(type="trigger",
                     args=[(x,y) for x,y in soup.attrs.items()])

    for child in soup.children:
        if child is None or isinstance(child, str):
            guarded_log("Skipping trigger: {}", child)
        elif child.name == "performancerealization":
            data.add_component(simple_tag_handler(child))
        elif "rule" in child.name:
            data.add_component(CSH.rule_handler(child))
        else:
            logging.info(f"Unknown trigger component: {child}")

    return data

def character_handler(soup):
    data = ParseBase(type="character",
                     name=soup.attrs['name'],
                     args=[(x,y) for x,y in soup.attrs.items() if x != "name"])

    for child in soup.children:
        if isinstance(child, str):
            guarded_log("Skipping character: {}", child)
            continue

        data.add_component(simple_tag_handler(child))

    return data


def simple_tag_handler(soup):
    args = [(x,y) for x,y in soup.attrs.items()]
    if soup.string is not None:
        args.append(("string", soup.string))
    data = ParseBase(type=soup.name,
                     args=args)
    return data
