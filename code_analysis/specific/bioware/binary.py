#!/usr/bin/env python3
"""
Construct.py based readers for bioware infinity engine file formats:
CHITIN.KEY
(todo) .BIF
(todo) .DLG
(todo) .TLK
(todo) .2DA
(todo) .BS
(todo) .BCS
(todo) .MAZE
(todo) .STR

https://gibberlings3.github.io/iesdp/file_formats/index.htm

Notes:
numbers are little endian
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

##-- utils
Word   = C.Int16ul
DWord  = C.Int32ul
OffStr = C.Struct(
    # Offset string
    "_pos" / C.Tell,
    C.Seek(C.this._.name_offset),
    "str"    / C.CString("ascii"),
    C.Seek(C.this._pos)
    )

##-- end utils

def build_key_format() -> C.Struct:
    """
    Build a construct parser for infinity engine KEY format file
    Structure:
    header, [bif descriptions], [resource descriptions]

    see:
    https://gibberlings3.github.io/iesdp/file_formats/ie_formats/key_v1.htm
    """
    key_header = C.Struct(C.Const(b"KEY"), C.Padding(1),
                            "version"    / C.FixedSized(4, C.NullStripped(C.GreedyString("ascii"))),
                            "bif_num"    / DWord,
                            "res_num"    / DWord,
                            "bif_offset" / DWord,
                            "res_offset" / DWord,
                            )

    bif_desc = C.Struct("pos" / C.Tell,
                        "id" / C.Computed(C.this._index),
                        "file_len"    / DWord,
                        "name_offset" / DWord,
                        "name"        / OffStr,
                        "name_len"    / Word,
                        "location"    / C.FlagsEnum(Word, data=1, cache=2, cd1=4, cd2=8, cd3=16, cd5=24, cd6=32),
        )

    resource_desc = C.Struct("id" / C.Computed(C.this._index),
                             "name"  / C.PaddedString(8, "ascii"),
                             "type"  / Word,
                             "index" / C.ByteSwapped(C.BitStruct(
                                 "bif" / C.BitsInteger(12),
                                 "tile" / C.BitsInteger(6),
                                 "file" / C.BitsInteger(14),
                             )))

    chitin_key = C.Struct("header" / key_header,
                          C.Seek(C.this.header.bif_offset),
                          "bif_descs" / bif_desc[C.this.header.bif_num],
                          C.Seek(C.this.header.res_offset),
                          "res_descs" / resource_desc[C.this.header.res_num]
                          )
    return chitin_key
