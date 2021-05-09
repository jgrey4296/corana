#!/usr/bin/env python3

from bs4 import BeautifulSoup
from collections import defaultdict

def verify_schema(soup, schema):
    assert(isinstance(schema, list))
    schema = [x.lower() for x in schema]
    all_actual = [x for x in soup.children if not isinstance(x, str)]

    assert(all([x.name.lower() in schema for x in all_actual])), breakpoint()

def infer_schema(soup, schema=None):
    """
    Given some xml, aggregate all tags and their children, into a rough schema
    """
    if schema is None:
        schema = defaultdict(lambda: set())

    for tag in soup.descendants:
        if isinstance(tag, str):
            continue

        schema[tag.name].update({x.name for x in tag.children if not isinstance(x, str)})

    return schema

def quick_infer_file(*filenames):
    schema = None
    for filename in filenames:
        with open(filename) as f:
            soup = BeautifulSoup(f.read(),
                                 features="lxml")

        schema = infer_schema(soup)

    return schema
