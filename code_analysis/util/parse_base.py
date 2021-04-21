#!/usr/bin/env python3
import argparse
import json
import logging as root_logger
from dataclasses import InitVar, dataclass, field
from enum import Enum
from fractions import Fraction
from os import listdir
from os.path import (abspath, exists, expanduser, isdir, isfile, join, split,
                     splitext)
from random import choice, shuffle
from time import sleep
from typing import (Any, Callable, ClassVar, Dict, Generic, Iterable, Iterator,
                    List, Mapping, Match, MutableMapping, Optional, Sequence,
                    Set, Tuple, TypeVar, Union, cast)

import requests

logging = root_logger.getLogger(__name__)


@dataclass
class ParseBase:
    """
    Base class of parse results, tracks line number position, and components
    """
    name       : str                  = field(default=None)
    type       : str                  = field(default=None)
    args       : List[str]            = field(default_factory=list)
    components : List[Dict[str, Any]] = field(default_factory=list)
    line_no    : int                  = field(default=-1)

    @staticmethod
    def reconstruct(text):
        return ParseBase()

    def __repr__(self):
        return "({} : {} : {})".format(self.line_no,
                                       self.type,
                                       self.name)

    def __str__(self):
        data    = {}
        pattern = "{} : {} : {} := {}"

        if bool(self.args):
            data.update({ 'args': [str(x) for x in self.args]})

        if bool(self.components):
            if not hasattr(self.components[0], 'to_dict'):
                data.update({ 'components' : [str(x) for x in self.components]})
            else:
                data.update({ 'components' : [x.to_dict() for x in self.components]})


        return pattern.format(self.line_no,
                              self.type,
                              self.name,
                              json.dumps(data))

    def __lt__(self, other):
        """ Compare by line number position """
        assert(isinstance(other, ParseBase))
        return self.line_no < other.line_no
