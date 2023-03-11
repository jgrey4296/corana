#!/usr/bin/env python3
"""
Tasks for generating code, such as XML and Json interfaces

"""
##-- imports
from __future__ import annotations

import abc
import logging as logmod
import pathlib as pl
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
# If CLI:
# logging = logmod.root
# logging.setLevel(logmod.NOTSET)
##-- end logging

import doot
from doot import globber

class GenXMLInterfaces(globber.DirGlobber):
    """
    (data -> [codegen, temp] Generate xml schemas
    """

    def __init__(self, name="codegen::xml", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task

class GenJsonInterfaces(globber.DirGlobber):
    """

    """

    def __init__(self, name="codegen::json", locs=None, roots=None, rec=True, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task
