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

import tomler
import doot
from doot import globber
from doot.mixins.delayed import DelayedMixin
from doot.mixins.targeted import TargetedMixin
from code_analysis.structs.binary import infinity
from code_analysis.mixins.path_mirror import PathMirrorMixin
from doot.mixins.filer import FilerMixin
from doot.mixins.zipper import ZipperMixin

dataset_marker = doot.config.on_fail(".zipthis.toml", str).dataset.marker()

class CADatasetGlobber(DelayedMixin, TargetedMixin, PathMirrorMixin, FilerMixin, ZipperMixin, globber.DootEagerGlobber):
    """
    Specialised globber for use with CA_datasets
    """
    select_tags      = []
    select_directory = False
    dataset_marker   = dataset_marker

    def set_params(self):
        return self.target_params() + [
            {"name": "tags", "long": "tags", "type":  lambda x: set(self.select_tags + x.split(",")), "default":  set(self.select_tags)}
        ]

    def filter(self, fpath):
        maybe_marker  = fpath / self.dataset_marker
        parent_marker = self.is_toml_tagged(self.parent_toml(fpath))

        if not (maybe_marker.exists() or parent_marker.exists()):
            return self.globc.noBut

        if maybe_marker.exists() and not self.is_toml_tagged(maybe_marker, *self.args['tags']):
            return self.globc.no

        if parent_marker.exists() and not self.is_toml_tagged(parent_marker, *self.args['tags']):
            return self.globc.no

        if self.select_directory and fpath.is_file():
            return self.globc.no

        if fpath.is_file() and fpath.suffix not in self.exts:
            return self.globc.no

        return self.globc.yes
