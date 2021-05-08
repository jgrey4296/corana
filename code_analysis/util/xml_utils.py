#!/usr/bin/env python3

def verify_schema(soup, schema):
    assert(isinstance(schema, list))
    schema = [x.lower() for x in schema]
    all_actual = [x for x in soup.children if not isinstance(x, str)]

    assert(all([x.name.lower() in schema for x in all_actual])), breakpoint()
