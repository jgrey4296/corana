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

import tomlguard
import doot
from doot import globber
from doot.mixins.delayed import DelayedMixin
from doot.mixins.targeted import TargetedMixin
from provenance.structs.binary import infinity
from provenance.mixins.marker_manip import MarkerManipulationMixin
from doot.mixins.filer import FilerMixin
from doot.mixins.zipper import ZipperMixin


class CADatasetGlobber(DelayedMixin, TargetedMixin, FilerMixin, ZipperMixin, globber.DootEagerGlobber, MarkerManipulationMixin):
    """
    Specialised globber for use with CA_datasets
    """
    select_tags      = []
    select_directory = False

    def set_params(self):
        return self.target_params() + [
            {"name": "tags", "long": "tags", "type":  lambda x: set(self.select_tags + x.split(",")), "default":  set(self.select_tags)}
        ]

    def filter(self, fpath):
        parent_marker = self.find_marker(fpath)

        # no markers found
        if not (parent_marker and parent_marker.exists()):
            return self.globc.noBut

        # in subdir of datase, but wrong tag
        if parent_marker and parent_marker.exists() and not self.is_marker_tagged(parent_marker, *self.args['tags']):
            return self.globc.no

        if (self.select_directory and fpath.is_file()) or (not self.select_directory and fpath.is_dir()):
            return self.globc.noBut

        if fpath.is_file() and fpath.suffix not in self.exts:
            return self.globc.no

        if self.select_directory and fpath.is_dir():
            return self.globc.yes

        return self.globc.yesAnd
