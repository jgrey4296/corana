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

##-- file types
infinity_file_types = {
    0x0001 : ".bmp",
    0x0002 : ".mve",
    0x0004 : ".wav",
    0x0005 : ".wfx",
    0x0006 : ".plt",
    0x03e8 : ".bam",
    0x03e9 : ".wed",
    0x03ea : ".chu",
    0x03eb : ".tis",
    0x03ec : ".mos",
    0x03ed : ".itm",
    0x03ee : ".spl",
    0x03ef : ".bcs",
    0x03f0 : ".ids",
    0x03f1 : ".cre",
    0x03f2 : ".are",
    0x03f3 : ".dlg",
    0x03f4 : ".2da",
    0x03f5 : ".gam",
    0x03f6 : ".sto",
    0x03f7 : ".wmp",
    0x03f8 : ".chr",
    0x03f9 : ".bs",
    0x03fa : ".chr",
    0x03fb : ".vvc",
    0x03fc : ".vef",
    0x03fd : ".pro",
    0x03fe : ".bio",
    0x03ff : ".wbm",
    0x0400 : ".fnt",
    0x0402 : ".gui",
    0x0403 : ".sql",
    0x0404 : ".pvrz",
    0x0405 : ".glsl",
    0x0408 : ".menu",
    0x0409 : ".menu",
    0x040a : ".ttf",
    0x040b : ".png",
    0x040c : ".bah",
    0x0802 : ".ini",
    0x0803 : ".src",
    }

##-- end file types

class BioWareInfinityBinaryMixin:
    """
    Mixin for building parts of infinity engine file formats

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
    file_types = infinity_file_types

    def build_key_v1_format(self) -> C.Struct:
        """
        Build a construct parser for infinity engine KEY format file
        Structure:
        header, [bif descriptions], [resource descriptions]

        see:
        https://gibberlings3.github.io/iesdp/file_formats/ie_formats/key_v1.htm
        """
        return C.Struct("header" / self._key_v1_header,
                        C.Seek(C.this.header.bif_offset),
                        "bif_descs" / self._key_v1_bif_description[C.this.header.bif_num],
                        C.Seek(C.this.header.res_offset),
                        "res_descs" / self._key_v1_resource_description[C.this.header.res_num]
                        )
    @property
    def _key_v1_header(self) -> C.Struct:
        return C.Struct(C.Const(b"KEY"), C.Padding(1),
                        "version"    / C.FixedSized(4, C.NullStripped(C.GreedyString("ascii"))),
                        "bif_num"    / self.DWord,
                        "res_num"    / self.DWord,
                        "bif_offset" / self.DWord,
                        "res_offset" / self.DWord,
                        )

    @property
    def _key_v1_bif_description(self) -> C.Struct:
        return C.Struct("pos" / C.Tell,
                        "id" / C.Computed(C.this._index),
                        "file_len"    / self.DWord,
                        "name_offset" / self.DWord,
                        "name"        / self.OffStr,
                        "name_len"    / self.Word,
                        "location"    / C.FlagsEnum(self.Word, data=1, cache=2, cd1=4, cd2=8, cd3=16, cd5=24, cd6=32),
            )

    @property
    def _key_v1_resource_description(self) -> C.Struct:
        return C.Struct("id" / C.Computed(C.this._index),
                        "name"  / C.PaddedString(8, "ascii"),
                        "type"  / self.Word,
                        "index" / C.ByteSwapped(C.BitStruct(
                            "bif" / C.BitsInteger(12),
                            "tile" / C.BitsInteger(6),
                            "file" / C.BitsInteger(14),
                        )))

    def TODO_build_bif_v1() -> C.Struct:
        """
        https://gibberlings3.github.io/iesdp/file_formats/ie_formats/bif_v1.htm
        """
        raise NotImplementedError()

    @property
    def _bif_v1_header(self) -> C.Struct:
        # 4 char: BIFF
        # 4 char: V1
        # 4 dword : file count
        # 4 dword : tile count
        # 4 dword : offset from start of file (SoF) to file entries
        raise NotImplementedError()

    @property
    def _bif_v1_entry(self) -> C.Struct:
        # 4 dword : resource key -> in chitin.key
        # 4 dword : offset from SoF to data
        # 4 dword : size of data
        # 2 word : file type
        # 2 word : unknown
        raise NotImplementedError()

    @property
    def _bif_v1_tile(self) -> C.Struct:
        # 4 dword : resource key -> in chitin.key
        # 4 dword : offset from SoF to data
        # 4 dword : tile count
        # 4 dword : tile size
        # 2 word : type (always 0x3eb)
        # 2 word : unknown
        raise NotImplementedError()

    def TODO_build_tlk_v1(self) -> C.Struct:
        """
        https://gibberlings3.github.io/iesdp/file_formats/ie_formats/tlk_v1.htm
        """
        raise NotImplementedError()

    @property
    def _tlk_v1_header(self) -> C.Struct:
        # 4 char : "TLK "
        # 4 char : "V1  "
        # 2 word : language id
        # 4 dword : number of strref's
        # 4 dword : offset from SoF to data
        raise NotImplementedError()

    @property
    def _tlk_v1_entries(self) -> C.Struct:
        # 2 word : bit field
        # 8 resref : resource name of sound
        # 4 dword : volume variance
        # 4 dword : pitch variance
        # 4 dword : offset from start of strref section
        # 4 dword : length of string
        raise NotImplementedError()

    @property
    def _tlk_v1_strings(self) -> C.Struct:
        # ascii encoded. not allways NULL terminated
        raise NotImplementedError()

    def TODO_build_dlg_v1(self) -> C.Struct:
        """
        https://gibberlings3.github.io/iesdp/file_formats/ie_formats/dlg_v1.htm
        """
        raise NotImplementedError()

    @property
    def _dlg_v1_header(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _dlg_v1_state_table(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _dlg_v1_transition_table(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _dlg_v1_state_triggers(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _dlg_v1_transition_triggers(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _dlg_v1_action_table(self) -> C.Struct:
        raise NotImplementedError()

    def TODO_build_2da_format() -> C.Struct:
        """
        https://gibberlings3.github.io/iesdp/file_formats/ie_formats/2da.htm
        """
        raise NotImplementedError()

    def TODO_build_src_format() -> C.Struct:
        """
        https://gibberlings3.github.io/iesdp/file_formats/ie_formats/src.htm
        """
        raise NotImplementedError()
