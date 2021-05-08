#!/usr/bin/env python3

def verify_schema(soup, schema):
    assert(isinstance(schema, list))
    assert(all([x.name.lower() in schema for x in soup.children]))
