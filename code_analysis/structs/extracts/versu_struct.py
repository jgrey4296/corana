#!/usr/bin/env python
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import logging as root_logger
logging = root_logger.getLogger(__name__)

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
        if bool(hand):
            self.args.append('hand_ordered')



