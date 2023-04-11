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
zip_marker = doot.config.on_fail(".zipthis.toml", str).zipper.marker()

class PathMirrorMixin:
    """
    Mixin to mirror raw directories -> extraction directories
    eg: data/raw/baldurs_gate/...    -> build/extractions/baldurs_gate/{extract_type}/...
    """

    def parent_toml(self, fpath) -> None|pl.Path:
        for parent in fpath.parents:
            parent_toml = parent / zip_marker
            if parent_toml.exists():
                return parent_toml

    def is_toml_tagged(self, fpath:None|pl.Path, *tags) -> bool:
        if fpath is None:
            return False

        assert(fpath.exists())
        data = tomler.load(fpath)
        toml_tags = data.on_fail([], list).dataset.instance.tags()
        return not bool(tags) or all([x in toml_tags for x in tags])

    def to_mirror(self, fpath:pl.Path, tag="_basic"):
        assert(fpath.is_relative_to(self.locs.data))
        file_name       = None
        dir_path        = fpath

        available_types = [x.name for x in self.locs.data.iterdir() if x.is_dir()]
        data_type = fpath.parts[1]
        assert(data_type in available_types)

        if fpath.is_file():
            file_name  = fpath.name if fpath.is_file() else None
            dir_path   = fpath.parent

        rel_path   = dir_path.relative_to(self.locs.data, data_type)
        in_extract = self.locs.extractions / rel_path.parts[0] / tag / rel_path.parts[1]

        if file_name is None:
            return in_extract

        return in_extract / file_name
