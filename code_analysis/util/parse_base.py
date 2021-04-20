#!/usr/bin/env python3
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

from dataclasses import dataclass, field, InitVar
from enum import Enum
from fractions import Fraction
from os import listdir
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from random import choice, shuffle
from time import sleep
import argparse
import json
import logging as root_logger
import requests
logging = root_logger.getLogger(__name__)


@dataclass
class ParseBase:
    """
    Base class of parse results, tracks line number position, and components
    """
    _type       : str                  = field(default=None)
    _name       : str                  = field(default=None)
    _args       : List[str]            = field(default_factory=list)
    _components : List[Dict[str, Any]] = field(default_factory=dict)
    _line_no    : int                  = field(default=-1)

    @staticmethod
    def reconstruct(text):
        return ParseBase()

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
