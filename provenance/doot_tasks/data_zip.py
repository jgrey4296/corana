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

from provenance.mixins.dataset_globber import CADatasetGlobber

class ReportData(CADatasetGlobber):
    """
    extract the zip marker and listings
    """

    def __init__(self, name="zip::report", locs=None, roots=None, output=None):
        super().__init__(name, locs, roots or [locs.SD_backup], rec=True)
        self.output = output or locs.build
        self.report_file = "data.report.toml"
        self.listing_file = "data.listing"

    def filter(self, fpath):
        if fpath.is_file() and fpath.suffix == ".zip" and self.zip_contains(fpath, self.dataset_marker):
            return self.globc.yes
        return self.globc.no

    def setup_detail(self, task):
        task.update({
                "actions" : [ (self.rmfiles, [self.output / self.report_file, self.output / self.listing_file]) ]
        })
        return task

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [
                (self.log, [f"Reporting {fpath}"], {"level":logmod.INFO}),
                (self.zip_unzip_concat, [self.output / self.report_file, fpath],  {"member" : zip_marker, 'header':f"\n\n------- {fpath}\n\n".encode()}),
                (self.zip_unzip_concat, [self.output / self.listing_file, fpath], {"member" : "."+fpath.with_suffix(".listing").name, 'header':f"\n\n------- {fpath}\n\n".encode()})
            ],
        })
        return task

class ZipCheck(CADatasetGlobber):
    """
    extract the zip marker and listings
    """

    def __init__(self, name="zip::check", locs=None, roots=None, output=None):
        super().__init__(name, locs, roots or [locs.SD_backup], rec=True)

    def filter(self, fpath):
        if not (fpath.is_file() or  fpath.suffix == ".zip"):
            return self.globc.no

        if fpath.is_file() and fpath.suffix == ".zip" and self.zip_contains(self.zip_marker):
            return self.globc.yes
        return self.globc.no

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [
                (self.log, [f"Checking: {fpath}"], {"level":logmod.INFO}),
                (self.zip_test, [fpath]),
            ],
        })
        return task

class UnzipData(CADatasetGlobber):
    """
    unzip data from sd backup. defaults to raw data
    """

    def __init__(self, name="zip::extract", locs=None, roots=None, output=None):
        super().__init__(name, locs, roots or [locs.SD_backup], rec=True)
        self.output = output or locs.data

    def set_params(self):
        return self.target_params() + [
            { "name": "members", "long": "members", "default": None, "type": str },
        ]

    def filter(self, fpath):
        if fpath.is_file() and fpath.suffix == ".zip": # and self.zip_contains(fpath, self.dataset_marker):
            return self.globc.yes
        return self.globc.noBut

    def subtask_detail(self, task, fpath):
        fn = None
        if self.args["members"] is not None:
            regex = re.compile(self.args['members'])
            fn    = lambda x: regex.search(x)
        elif (self.output / fpath.stem).exists():
            logging.error("Extraction Target already exists: %s", self.output / fpath.stem)
            return None

        task.update({
            "actions" : [
                (self.log, [f"Unzipping: {fpath}"], {"level":logmod.INFO}),
                (self.zip_unzip_to, [self.output, fpath], {"fn" : fn})
            ],
        })
        return task

class ZipData(CADatasetGlobber, BatchMixin):
    """
    For each datset marker, create a zipfile for it
    """

    def __init__(self, name="zip::compress", locs=None, roots=None, output=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)
        self.output = output or locs.backup

    def set_params(self):
        return super().set_params() + [
            {"name": "rezip", "long": "rezip", "type": bool, "default": False}
        ]

    def filter(self, fpath):
        if fpath.is_dir() and (fpath / self.dataset_marker).exists():
            return self.globc.yes
        return self.globc.noBut

    def subtask_detail(self, task, fpath):
        maybe_rm_zip = None
        if self.args['rezip']:
            maybe_rm_zip = (self.rmfiles, [self.calc_zip_path(fpath)])

        task.update({
            "actions": [
                maybe_rm_zip,
                (self.zip_data, [fpath]),
            ],
        })

        return task

    def zip_data(self, fpath):
        target_path = self.calc_zip_path(fpath)
        self.mkdirs(target_path.parent)
        self.zip_set_root(fpath)
        self.zip_globs(target_path, "**/*")

    def calc_zip_path(self, fpath):
        root = self.rel_path(fpath).with_suffix(".zip").name
        base = self.output / root
        return base
