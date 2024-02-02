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
class CoranaMetadata:

    name         : str                     = field()
    tags         : set[str]                = field()
    source       : set[str]                = field()
    count        : int                     = field()
    file_types   : set[str]                = field()
    notes        : list[str]               = field()
    initial_date : datetime.datetime       = field()

    log          : list[CoranaLog]     = field()
    subgroups    : list[CoranaSubData] = field()

    @staticmethod
    def from_dict(data:dict|TomlGuard) -> CoranaMetadata:
        raise NotImplementedError()

@dataclass
class CoranaLog:
    @staticmethod
    def from_dict(data:dict|TomlGuard) -> CoranaMetadata:
        raise NotImplementedError()

@dataclass
class CoranaDataTransformLog:

    @staticmethod
    def from_dict(data:dict|TomlGuard) -> CoranaDataTransformLog:
        raise NotImplementedError()


@dataclass
class CoranaEnvironment:

    @staticmethod
    def from_dict(data:dict|TomlGuard) -> CoranaEnvironment:
        raise NotImplementedError()

@dataclass
class CoranaListing:
    pass
