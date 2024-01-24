#!/usr/bin/env python3
"""


See EOF for license/metadata/notes as applicable
"""

##-- builtin imports
from __future__ import annotations

# import abc
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import weakref
# from copy import deepcopy
# from dataclasses import InitVar, dataclass, field
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable, Generator)
from uuid import UUID, uuid1

##-- end builtin imports

##-- lib imports
import more_itertools as mitz
##-- end lib imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging
printer = logmod.getLogger("doot._printer")

import stat
import doot
import doot.errors
from doot.structs import DootKey
from doot.mixins.task.zipper import ZipperMixin
import sh

from_key   = DootKey("from")
update_key = DootKey("update_")
target_key = DootKey("target")

basic_find = sh.find
provenance_dir = ".provenance"
provenance_file = ".provenance-meta.toml"
cruft_files = [".DS_Store"]


def readonly_raw(spec,state):
    """ Action to change permissions of all non-meta files in data/raw to read-only """
    root       = doot.locs["{raw}"]
    writable   = [pl.Path(x) for x in basic_find(root, "-perm", "-u=w").split("\n")]
    not_dir    = lambda x: not x.is_dir()
    not_meta   = lambda x: provenance_dir not in x.parts
    not_toml   = lambda x: provenance_file not in x.parts
    not_cruft  = lambda x: not any(x.name ==  y for y in cruft_files)

    applicable = list(filter(lambda x: not_dir(x) and not_meta(x) and not_toml(x) and not_cruft(x), writable))
    printer.info("Found writable raw files: ")
    printer.info("%s", "\n".join(str(x) for x in applicable[:50]))

    for fpath in applicable:
        printer.debug("TODO: (%s).chmod(stat.S_IREAD)", fpath)
        # fpath.chmod(stat.S_IREAD)

def gather_data(spec, state):
    target = from_key.to_path(spec, state)
    update = update_key.redirect(spec)
    printer.info("Gathering from: %s", target)
    zips = list(target.rglob("*.zip"))
    printer.info("Found: %s", len(zips))
    return { update : zips }

def cli_or_select(spec, state):
    update = update_key.redirect(spec)
    target = target_key.to_type(spec, state)
    source = from_key.to_type(spec, state)

    if target is None:
        selected = input("Select: ")
        raise NotImplementedError("TODO: select from globbed")

    filtered = list(sorted(x for x in source if target in x.stem))
    printer.info("-- Matching: ")
    printer.info("%s", "\n".join(x.name for x in filtered))
    printer.info("")
    printer.info("Count: %s", len(filtered))

    return { update : filtered }


class UnpackData(ZipperMixin):
    def __call__(self, spec, state):
        source = from_key.to_type(spec, state, type_=list)
        target_root = doot.locs["{data}"]

        for data in source:
            base_name    = data.stem
            shadow       = data.parent.name
            unpacked_loc = target_root / shadow
            if (unpacked_loc / base_name).exists():
                printer.warning("Unpack Target Destination already exists, not unpacking: %s", unpacked_loc/base_name)
                continue

            printer.info("Unpacking from %s to: %s", data, unpacked_loc)

            self.zip_unzip_to(unpacked_loc, data)

class PackData(ZipperMixin):
    def __call__(self, spec, state):
        source = from_key.to_type(spec, state, type_=list)
        target_root = doot.locs["{backup}"]

        for data in source:
            if data.name != provenance_file:
                printer.error("Bad pack data target", data)
                continue

            base_name    = f"{data.parent.name}.zip"
            shadow       = data.parent.name
            packed_loc   = target_root / shadow
            if (packed_loc / base_name).exists():
                printer.warning("Data pack Target Destination already exists, not packing: %s", packed_loc/base_name)
                continue

            printer.info("Packing data from %s to: %s", data, packed_loc)

            self.zip_set_root(data.parent)
            self.zip_globs(packed_loc/base_name, "**")
