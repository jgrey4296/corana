#!/usr/bin/env python3
"""
Construct.py based readers for bioware aurora engine file formats

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

class BioWareAuroraBinaryMixin:

    def TODO_build_gff_v3_3_format(self) -> C.Struct:
        """
        http://www.datoolset.net/wiki/GFF
        https://witcher-games.fandom.com/wiki/GFF_V3.3_format
        """
        raise NotImplementedError()

    @property
    def _gff_v3_3_header(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _gff_v3_3_struct_array(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _gff_v3_3_field_array(self) -> C.Struct:
        raise NotImplementedError()

    @property
    def _gff_v3_3_data_block(self) -> C.Struct:
        raise NotImplementedError()

    def TODO_build_gda_format(self) -> C.Struct:
        """
        http://www.datoolset.net/wiki/GDA
        """
        raise NotImplementedError()

    def TODO_build_key_v1_1_format(self) -> C.Struct:
        """
        https://witcher-games.fandom.com/wiki/KEY_BIF_V1.1_format
        """
        raise NotImplementedError()

    def TODO_build_bif_v1_1_format(self) -> C.Struct:
        """
        https://witcher-games.fandom.com/wiki/KEY_BIF_V1.1_format
        """
        raise NotImplementedError()

    def TODO_build_dlg_v3_3_format(self) -> C.Struct:
        """
        https://witcher-games.fandom.com/wiki/DLG_format
        """
        raise NotImplementedError()

    def TODO_build_qst_format(self) -> C.Struct:
        """
        https://witcher-games.fandom.com/wiki/QST_format
        """
        raise NotImplementedError()

    def TODO_build_tlk_v2(self) -> C.Struct:
        """
        http://www.datoolset.net/wiki/TLK
        http://www.datoolset.net/wiki/TLK_(DA2)
        """
        raise NotImplementedError()
