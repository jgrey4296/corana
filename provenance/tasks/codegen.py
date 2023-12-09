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

import doot
from provenance.mixins.dataset_globber import CADatasetGlobber

class GenXMLInterfaces(CADatasetGlobber):
    """
    (data -> [codegen, temp] Generate xml schemas
    """

    def __init__(self, name="codegen::xml", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [], rec=rec, exts=exts or [".xml"])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task

class GenJsonInterfaces(CADatasetGlobber):
    """

    """

    def __init__(self, name="codegen::json", locs=None, roots=None, rec=True, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [".json"])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task
