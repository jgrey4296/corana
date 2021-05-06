#!/usr/bin/env python3
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import logging as root_logger
logging = root_logger.getLogger(__name__)

from dataclasses import dataclass, field, InitVar

@dataclass
class ParseState:
    bracket_count  : int       = field(default=0)
    line           : int       = field(default=0)

    block_text     : str       = field(default=None)
    current        : Any       = field(default=None)
    def_prefix     : Any       = field(default=None)
    fold_into_last : bool      = field(default=False)
    in_block       : List[Any] = field(default_factory=list)
    in_def         : Any       = field(default=None)
    last_line      : Any       = field(default=None)

    def inc_line(self):
        self.line += 1
