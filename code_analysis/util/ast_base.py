#/usr/bin/env python3
"""

"""
##-- imports
from __future__ import annotations

import abc
import logging as logmod
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from re import Pattern
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable)
from uuid import UUID, uuid1
from weakref import ref

if TYPE_CHECKING:
    # tc only imports
    pass
##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##-- util context manager
class ASTContextManager:
    """ For ensuring all ASTs are built with the correct source """

    def __init__(self, parse_source):
        self.parse_source = parse_source

    def __enter__(self):
        ASTBase.current_parse_source = self.parse_source

    def __exit__(self, exc_type, exc_value, exc_traceback):
        ASTBase.current_parse_source = None


##-- end util context manager

@dataclass(frozen=True)
class ASTBase:

    loc    : tuple[int, int]                  = field(default=None, kw_only=True)
    source : str                              = field(init=False, repr=False)

    current_parse_source : ClassVar[None|str] = None

    def __post_init__(self):
        if ASTBase.current_parse_source is not None:
            self.source = ASTBase.current_parse_source

    @staticmethod
    def manage_source(parse_source):
        return ASTContextManager(parse_source)
