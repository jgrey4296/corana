#!/usr/bin/env python3
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
logging = root_logger.getLogger(__name__)

class ParseBase:
    """
    Base class of parse results, tracks line number position, and components
    """

    def __init__(self):
        self._type = None
        self._name = None
        self._components = []
        self._args = []
        self._line_no = -1

    def __repr__(self):
        return "({} : {} : {})".format(self._line_no,
                                       self._type,
                                       self._name)

    def __str__(self):
        data = {}

        if bool(self._args):
            data.update({ 'args': [str(x) for x in self._args]})

        if bool(self._components):
            if not hasattr(self._components[0], 'to_dict'):
                data.update({ 'components' : [str(x) for x in self._components]})
            else:
                data.update({ 'components' : [x.to_dict() for x in self._components]})

        s = "{} : {} : {} := {}"

        return s.format(self._line_no,
                        self._type,
                        self._name,
                        json.dumps(data))

    def __lt__(self, other):
        """ Compare by line number position """
        assert(isinstance(other, ParseBase))
        return self._line_no < other._line_no
