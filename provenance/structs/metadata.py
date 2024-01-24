#!/usr/bin/env python3
"""
See EOF for license/metadata/notes as applicable
"""

##-- builtin imports
from __future__ import annotations

# import abc
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import weakref
# from copy import deepcopy
# from dataclasses import InitVar, dataclass, field
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable, Generator)
from uuid import UUID, uuid1

##-- end builtin imports

##-- lib imports
import more_itertools as mitz
##-- end lib imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

import tomlguard
import doot
import doot.errors

@dataclass
class ProvenanceMetadata:

    name         : str                     = field()
    tags         : set[str]                = field()
    source       : set[str]                = field()
    count        : int                     = field()
    file_types   : set[str]                = field()
    notes        : list[str]               = field()
    initial_date : datetime.datetime       = field()

    log          : list[ProvenanceLog]     = field()
    subgroups    : list[ProvenanceSubData] = field()

    @staticmethod
    def from_dict(data:dict|TomlGuard) -> ProvenanceMetadata:
        raise NotImplementedError()

@dataclass
class ProvenanceLog:
    @staticmethod
    def from_dict(data:dict|TomlGuard) -> ProvenanceMetadata:
        raise NotImplementedError()

@dataclass
class ProvenanceDataTransformLog:

    @staticmethod
    def from_dict(data:dict|TomlGuard) -> ProvenanceDataTransformLog:
        raise NotImplementedError()


@dataclass
class ProvenanceEnvironment:

    @staticmethod
    def from_dict(data:dict|TomlGuard) -> ProvenanceEnvironment:
        raise NotImplementedError()

@dataclass
class ProvenanceListing:
    pass
