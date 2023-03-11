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

from gff import gff_parser
from gff.gff_struct import gff_struct
import mmap
import multiprocessing
import os
import sys
import time


def main():
    file_path   = "singleplayer_en-us.tlk"
    gff         = gff_struct.parse_file(file_path)
    data_struct = gff_parser.generate_tree_struct(gff)
    data        = data_struct.parse_file(file_path)


    with open(file_path, "r+b") as f, mmap.mmap(f.fileno(), 0) as mm:
        # for conversation_line in data.CONVERSATION_LINE_LIST.List.reference_data.GenericWrapper:
            # offset = int(conversation_line.reference_data.CONVERSATION_LINE_TEXT.TLKString.ECString.offset)
            # tell   = int(conversation_line.reference_data.CONVERSATION_LINE_TEXT.TLKString.ECString.tell)
            # text = conversation_line.reference_data.CONVERSATION_LINE_TEXT
            # tlk = text.TLKString
            # ec = tlk.ECString
            # length = int(conversation_line.reference_data.CONVERSATION_LINE_TEXT.TLKString.ECString.reference_data.length)

        for talk_string in data.TALK_STRING_LIST.List.reference_data.STRN:
            offset = int(talk_string.TALK_STRING.ECString.offset)

            if talk_string.TALK_STRING.ECString.reference_data is not None:
                print(talk_string.TALK_STRING.ECString.reference_data.string_data)


##-- ifmain
if __name__ == "__main__":
    main()
##-- end ifmain
