#!/usr/bin/env python
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

from dataclasses import dataclass, field, InitVar

from code_analysis.util.parse_base import ParseBase
from enum import Enum

versu_e = Enum('Versu Enums', 'COMMENT COPEN CCLOSE ODEF CDEF TOPEN END PATCH RANDOM')
Enum_to_String = {
    versu_e.TOPEN  : "type",
    versu_e.PATCH  : "patch",
    versu_e.RANDOM : "random"
    }

@dataclass
class VersuBlock(ParseBase):

    def __post_init__(self):
        if self.type in Enum_to_String:
            self.type = Enum_to_String[self.type]
        else:
            logging.warning("Non-Enum Block Type: {}".format(str(self.type)))



@dataclass
class VersuExpression(ParseBase):
    hand : InitVar[Any] = field(default=None)

    def __post_init__(self, hand):
        self._block = None
        if bool(hand):
            self.args.append('hand_ordered')




##------
@dataclass
class TempData:
    """ Intermediary parse data """
    comments      : int       = field(default=0)
    non_exclusion : int       = field(default=0)
    exclusions    : int       = field(default=0)
    strings       : List[Any] = field(default_factory=list)
    in_order      : List[Any] = field(default_factory=list)

    blocks        : List[Any] = field(default_factory=list)
    functions     : List[Any] = field(default_factory=list)
    inserts       : List[Any] = field(default_factory=list)
    types         : List[Any] = field(default_factgory=list)
    actions       : List[Any] = field(default_factory=list)

@dataclass
class ParseState:
    bracket_count  : int       = field(default=0)
    current        : Any       = field(default=None)
    line           : int       = field(default=0)
    in_block       : List[Any] = field(default_factory=list)
    block_text     : str       = field(default=None)
    in_def         : Any       = field(default=None)
    def_prefix     : Any       = field(default=None)
    last_line      : Any       = field(default=None)
    fold_into_last : bool      = field(default=False)
