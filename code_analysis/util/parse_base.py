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
from uuid import UUID, uuid1
import json
import requests

logging = root_logger.getLogger(__name__)


PATTERN = "{} : {} : {} := {}"

@dataclass
class ParseBase:
    """
    Base class of parse results, tracks line number position, and components
    """

    name       : str                  = field(default=None)
    type       : str                  = field(default=None)
    line_no    : int                  = field(default=-1)
    args       : List[str]            = field(default_factory=list)
    components : List['ParseBase'] = field(default_factory=list)
    uuid       : UUID                 = field(init=False, default_factory=uuid1)

    @staticmethod
    def reconstruct(text):
        # TODO
        simple, data_s = text.split(":=")
        line_no, type, name = simple.split(":")
        args = []
        components = []
        data = json.loads(data_s)
        if 'args' in data:
            args += data['args']
        if 'components' in data:
            components += data['components']

        return ParseBase(name, type,
                         line_no=line_no,
                         args=args,
                         components=components)

    def __repr__(self):
        return "({} : {} : {})".format(self.line_no,
                                       self.type,
                                       self.name)

    def __str__(self):
        data    = {"args"       : [],
                   "components" : []}

        if bool(self.args):
            data['args'] += [str(x) for x in self.args]

        if bool(self.components):
            if not hasattr(self.components[0], 'to_dict'):
                data['components'] += [str(x) for x in self.components]
            else:
                data['components'] += [x.to_dict() for x in self.components]


        return PATTERN.format(self.line_no,
                              self.type,
                              self.name,
                              json.dumps(data))

    def to_dict(self):
        components = [x.to_dict() for x in self.components]

        return {"name" : self.name,
                "type" : self.type,
                "line_no" : self.line_no,
                "args" : self.args,
                "components" : components,
                "uuid" : str(self.uuid)
                }

    def dumps(self):
        return json.dumps(self.to_dict(),
                          indent=4)

    def __lt__(self, other):
        """ Compare by line number position """
        assert(isinstance(other, ParseBase))
        return self.line_no < other.line_no


    def add_component(self, comp):
        self.components.append(comp)
