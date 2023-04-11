#!/usr/bin/env python3
"""

"""
##-- imports
from __future__ import annotations

import types
import abc
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable)
from uuid import UUID, uuid1
from weakref import ref

##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

import construct as C


class BethesdaBinaryMixin:
    """

    """
    Word   = C.Int16ul
    DWord  = C.Int32ul
    # Offset string
    OffStr = C.Struct(
        "_pos" / C.Tell,
        C.Seek(C.this._.name_offset),
        "str"    / C.CString("ascii"),
        C.Seek(C.this._pos)
        )

    def build_esm_format(self):
        raise NotImplementedError()
