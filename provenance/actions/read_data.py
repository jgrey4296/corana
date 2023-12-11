#!/usr/bin/env python3
"""
Utility actions for standard format loading.
  eg: csv, json...

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

import doot
import doot.errors
import doot.util.expansion as exp
import pandas


def read_csv(spec, state):
    """ A Basic loader for csv data into a pandas dataframe """
    update            = exp.to_str(spec.kwargs.on_fail("data").update_(), spec, state, indirect=True)
    path              = exp.to_path(spec.kwargs.on_fail("_from").from_(), spec, state, indirect=True)
    frame : DataFrame = pandas.read_csv(data, skip_blank_lines=True, sep=",", skiprows=5)
    return { update : frame }


"""


"""
