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

import zipfile
import re
import fileinput
import datetime
import zlib
import ast
import hashlib

import doot
from doot import tasker, globber
from doot.tasks.groups import *
from doot.tasks.groups_secondary import *
from doot.tasks.files.backup import BackupTask
from doot.mixins.delayed import DelayedMixin
from doot.mixins.zipper import ZipperMixin
from doot.mixins.batch import BatchMixin
from doot.mixins.targeted import TargetedMixin
from doot.mixins.filer import FilerMixin

from corana.mixins.dataset_globber import CADatasetGlobber

dataset_marker = doot.config.on_fail(".zipthis.toml", str).dataset.marker()

class DataListing(CADatasetGlobber, BatchMixin):
    """
    Generate file listings for datasets
    """

    select_directory = True

    def __init__(self, name="list::data", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)

    def subtask_detail(self, task, fpath):
        task.update({
            "actions": [ (self.generate_listing, [fpath]) ],
        })
        return task

    def generate_listing(self, fpath):
        logging.info(f"Generating Listing for {fpath}")
        listing_file = fpath / f".{fpath.name}.listing"
        # TODO maybe use self.glob_target to ignore files
        all_files    = [x.relative_to(fpath) for x in fpath.rglob("*") if x.is_file() and x.name not in [dataset_marker, ".DS_Store"]]

        for zipf in fpath.rglob("*.zip"):
            relative = zipf.relative_to(fpath)
            with zipfile.ZipFile(zipf) as zz:
                all_files += [relative / x for x in zz.namelist()]

        count        = len(all_files)
        suffixes     = ", ".join({f"\"{x.suffix}\"" for x in all_files if bool(x.suffix)})
        listing_str  = "\n".join(sorted(str(x) for x in all_files))

        listing_file.write_text(listing_str)

        count_re = re.compile(r"^count\s+=\s+\d+")
        types_re = re.compile(r"^file_types\s+=\s+")
        for line in fileinput.input(files=[fpath / dataset_marker], inplace=True):
            if count_re.match(line):
                print(f"count = {count}")
            elif types_re.match(line):
                print(f"file_types = [{suffixes}]")
            else:
                print(line, end="")

class SplitRootListings(tasker.DootTasker):
    """
    Split root listings into subdir files
    """

    def __init__(self, name="list::split.root", locs=None, roots=None):
        super().__init__(name, locs)

    def task_detail(self, task):
        task.update({
            "actions" : [
                self.process,
            ]
        })
        return task

    def process(self):
        (self.locs.build / "split_listings").mkdir()
        globbed = list(self.locs.root_listings.glob("*.ls"))
        if not bool(globbed):
            return

        for line in fileinput.input(files=globbed):
            try:
                lpath  = pl.Path(line)
                parts  = lpath.parts
                if parts[1] == ".DS_Store":
                    continue

                rel_path = lpath.relative_to(parts[0])
                target   = parts[1].replace(" ", "_").lower()
                with open(self.locs.build / "split_listings" / f"{target}.ls", 'a') as f:
                    f.print(str(rel_path))

            except IndexError:
                pass
