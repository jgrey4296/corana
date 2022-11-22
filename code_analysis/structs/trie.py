#!/usr/bin/env python3
##-- imports
import argparse
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from time import sleep
from fractions import Fraction
from random import choice, shuffle
import json
from enum import Enum
import logging as root_logger
import requests
##-- end imports

logging = root_logger.getLogger(__name__)

class Trie:
    """
    A Simple Trie structure
    """


    def __init__(self, value, path, example=None):
        self.count = 0
        self.value = value
        self.path = "{} {}".format(path, value)
        self.data = {}
        self._example = example

    def __repr__(self):
        #Print all paths to leaves
        return "\n".join(self.leaves())

    def __bool__(self):
        """ Is Node populated? """
        return bool(self.data)

    def get(self, key):
        if key not in self.data:
            self.data[key] = Trie(key, self.path)

        return self.data[key]

    def inc(self):
        self.count += 1

    def add_string(self, theList, transform=None, example=None):
        if transform is None:
            transform = lambda x: x
        current = self
        for val in theList:
            val_prime = transform(val)
            current = current.get(val_prime)
            current.inc()
        if example and current._example is None:
            current._example = example

    def leaves(self):
        leaves = []
        queue = [self]
        while queue:
            node = queue.pop(0)
            if not node:
                leaves.append("{} :: {} / {} : {}".format(node.path, node.count.numerator, node.count.denominator, node._example))
            else:
                queue += list(node.data.values())

        return leaves

    def convert_to_rational(self, total_count):
        if not isinstance(self.count, Fraction):
            self.count = Fraction(self.count, total_count)
        total_count = sum([x.count for x in self.data.values()])
        for x in self.data.values():
            x.convert_to_rational(total_count)


    def construct_likely_path(self):
        path = ""
        current = self
        while bool(self):
            children = list(self.data.values())
            prob_pairs = [(x.count, x) for x in children]

            #random selection
            current = prob_pairs[0][1]
            path += " {} ({}) ".format(current.key, str(current.count))

        return path
