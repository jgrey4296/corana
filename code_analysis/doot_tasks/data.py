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
import zipfile
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
from doot.tasks.files import listing
from doot.tasks.files.backup import BackupTask
from doot.mixins.delayed import DelayedMixin
from doot.mixins.zipper import ZipperMixin
from doot.mixins.batch import BatchMixin
from doot.mixins.targeted import TargetedMixin

zip_marker = doot.config.on_fail(".zipthis.toml", str).tool.doot.zipper.marker()

class BackupZips(BackupTask):
    """
    Copy all zipped data to external sd card
    """

    def __init__(self, name="data::backup", locs=None):
        super().__init__(name, locs, [locs.backup], output=locs.SD_backup)

class ZipData(DelayedMixin, TargetedMixin, globber.DootEagerGlobber, ZipperMixin, BatchMixin):
    """
    For each zipmarker, create a zipfile for it
    """

    def __init__(self, name="data::zip", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)
        self.output = locs.backup

    def set_params(self):
        return self.target_params()

    def subtask_detail(self, task, fpath):
        task.update({
            "actions": [
                (self.zip_data, [fpath]),
            ],
        })
        return task

    def filter(self, fpath):
        if fpath.is_dir() and (fpath / zip_marker).exists():
            return self.control.keep
        return self.control.discard

    def zip_data(self, fpath):
        target_path = self.calc_zip_path(fpath)
        self.mkdirs(target_path.parent)
        self.zip_set_root(fpath)
        self.zip_create(target_path)
        self.zip_globs(target_path, str(fpath / "**/*"))

    def calc_zip_path(self, fpath):
        root = self.locs.data
        base = self.output / fpath.relative_to(root).with_suffix(".zip")
        return base

class TomlSummary(DelayedMixin, TargetedMixin, globber.DootEagerGlobber, BatchMixin):
    """
    Find all zip markers, and add the basic toml structure for them
    """

    def __init__(self, name="data::tomlise", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)

    def set_params(self):
        return self.target_params()

    def filter(self, fpath):
        zip_f = fpath / zip_marker
        if fpath.is_dir() and zip_f.exists():
            if zip_f.stat().st_size == 0:
                logging.info(f"Found Empty Toml: {fpath}")
                return self.control.keep
            else:
                logging.info(f"Populated Toml: {fpath}")

        return self.control.discard

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [
                (self.prepare_toml, [fpath]),
            ]
        })
        return task

    def prepare_toml(self, fpath):
        logging.info(f"Preparing Dataset Toml: {fpath}")
        existing_text : str           = (fpath / zip_marker).read_text().strip()
        files         : list[pl.Path] = list(fpath.rglob("*"))
        exts          : set[str]      = set(f"\"{x.suffix}\"" for x in files if bool(x.suffix))
        toml_lines    : list[str]     = []
        now           : str           = datetime.datetime.now().isoformat()

        # Hand write the toml... for now
        toml_lines.append("[dataset.instance] # A Data Summary for integrity")
        toml_lines.append(f"name         = \"{fpath.stem}\" # A Name to refer to this data. Default: directory name")
        toml_lines.append("tags          = [] # Tags to collect different datasets together")
        toml_lines.append("source        = [] # Where its from")
        toml_lines.append(f"count         = {len(files)} # Number of files in dataset")
        toml_lines.append("file_types    = [ " + ", ".join(exts) + " ] # Extensions of files in dataset")
        toml_lines.append("data-zip-hash = \"TODO\" # md5 hash of the files in listing zipped together")
        toml_lines.append("")
        toml_lines.append(f"[dataset.log] # Recording things done to this data")
        toml_lines.append(f"initial-date = \"{now}\" # When this summary was created")
        toml_lines.append("preprocessing = [] # Things done to data before it was added")
        toml_lines.append("")
        toml_lines.append("# Subgroups of the files of particular interest")
        toml_lines.append("[[dataset.subgroup]]")

        toml_lines.append("# Additional")
        toml_lines.append(existing_text)
        text = "\n".join(toml_lines)
        self.verify_toml(text)
        (fpath / zip_marker).write_text(text)

    def verify_toml(self, text):
        # TODO
        pass

class TomlConcat(tasker.DootTasker):
    """
    Combine all zip_markers
    """

    def __init__(self, name="data::concat", locs=None):
        super().__init__(name, locs)
        self.output = locs.build / "datasets.toml"

    def task_detail(self, task):
        task.update({
            "actions" : [ self.append_all_dataset_summaries ],
        })
        return task

    def append_all_dataset_summaries(self):
        globbed = list(self.locs.data.rglob(zip_marker))
        last    = None
        with open(self.output, 'a') as f:
            for line in fileinput.input(files=globbed):
                if fileinput.filename() != last:
                    last = fileinput.filename()
                    print(f"\n#-------------------- {fileinput.filename()}", file=f)
                    print("[[dataset]]\n", file=f)

                print(line, end="", file=f)

class TomlAdjust(tasker.DootTasker):
    """
    run line adjustment on dataset tomls
    """

    def __init__(self, name="data::adjust", locs=None, processor=None):
        super().__init__(name, locs)
        self.dataset_re = re.compile(r"^\[dataset\]")
        self.listing_re = re.compile(r"^listing\s+=\s+(\[.+?\])")
        self.hash_re    = re.compile(r"^data-zip-hash")
        self.processor  = processor

    def filter(self, fpath):
        if fpath.name == zip_marker:
            return self.control.keep
        return self.control.discard

    def set_params(self):
        return [
            { "name": "processor", "short": "p", "type": str, "default": None }
        ]

    def task_detail(self, task):
        match self.args['processor']:
            case None if callable(self.processor):
                pass
            case str() as x if hasattr(self, x):
                self.processor = getattr(self, x)
            case _:
                logging.warning("Data Adust needs a processor specified")
                return None

        task.update({
            "actions": [
                self.adjust_tomls,
            ],
        })
        return task

    def adjust_tomls(self):
        globbed = list(self.locs.data.rglob(zip_marker))
        for line in fileinput.input(files=globbed, inplace=True):
            if not self.processor(self, line):
                print(line, end="")

    def adjust_head(self, line):
        if not self.dataset_re.match(line):
            return False

        print("[dataset.instance] # A Data Summary for Integrity")
        return True

    def adjust_listing(self, line):
        maybe_match = self.listing_re.match(line)
        if not maybe_match:
            return False

        print("")
        return True

    def add_zip_hash(self, line):
        maybe_match = self.hash_re.match(line)
        if not maybe_match:
            return False

        filename =  pl.Path(fileinput.filename()).parent.relative_to(self.locs.data).with_suffix(".zip")
        target = self.locs.backup / filename
        assert(target.exists()), target
        with open(target, 'rb') as f:
            digest = hashlib.file_digest(f, "sha256").hexdigest()

        print(f"data-zip-sha256 = \"{digest}\"")
        return True

class TomlAge(tasker.DootTasker):

    def __init__(self, name="data::age", locs=None):
        super().__init__(name, locs)
        self.data = []

    def task_detail(self, task):
        task.update({
            "actions" : [
                self.glob_data,
                self.sort_data,
                self.report_data,
            ]
        })
        return task

    def glob_data(self):
        self.data = list(self.locs.data.rglob(zip_marker))

    def sort_data(self):
        self.data.sort(key=lambda x: x.stat().st_mtime)

    def report_data(self):
        report = [
            "Oldest",
            "------------------------------",
            ]
        report += [str(x) for x in self.data]
        report += [
            "------------------------------",
            "Youngest"
            ]

        (self.locs.build / "data_desc_age.sort").write_text("\n".join(report))

class TomlTagless(tasker.DootTasker):

    def __init__(self, name="data::tagless", locs=None):
        super().__init__(name, locs)
        self.globbed = []
        self.data    = []

    def task_detail(self, task):
        task.update({
            "actions" : [
                self.glob_data,
                self.read_data,
                self.report_data,
            ]
        })
        return task

    def glob_data(self):
        self.globbed = list(self.locs.data.rglob(zip_marker))

    def read_data(self):
        tag_re = re.compile(r"^tags\s+=\s+\[(.*?)\]")

        for line in fileinput.input(files=self.globbed):
            res = tag_re.match(line)
            if res is None:
                continue
            if res and len(res[1].strip()) == 0:
                logging.info(f"Found: {fileinput.filename()} : {res[1]}")
                self.data.append(fileinput.filename())

            fileinput.nextfile()

    def report_data(self):
        report = [
            "Datasets missing tags",
            "------------------------------",
            ]
        report += sorted([str(x) for x in self.data])

        (self.locs.build / "data_desc_tagless").write_text("\n".join(report))

class DataListing(DelayedMixin, TargetedMixin, globber.DootEagerGlobber, BatchMixin):
    """
    Generate file listings for datasets
    """

    def __init__(self, name="data::listings", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)

    def filter(self, fpath):
        if fpath.is_dir() and (fpath / zip_marker).exists():
            return self.control.keep

        return self.control.discard

    def set_params(self):
        return self.target_params()

    def subtask_detail(self, task, fpath):
        task.update({
            "actions": [ (self.generate_listing, [fpath]) ],
        })
        return task

    def generate_listing(self, fpath):
        logging.info(f"Generating Listing for {fpath}")
        listing_file = fpath / f".{fpath.name}.listing"
        # TODO maybe use self.glob_target to ignore files
        all_files    = [x.relative_to(fpath) for x in fpath.rglob("*") if x.is_file() and x.name not in [zip_marker, ".DS_Store"]]

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
        for line in fileinput.input(files=[fpath / zip_marker], inplace=True):
            if count_re.match(line):
                print(f"count = {count}")
            elif types_re.match(line):
                print(f"file_types = [{suffixes}]")
            else:
                print(line, end="")

class DataCrawl(DelayedMixin, globber.DootEagerGlobber):
    """
    Scraper for raw directories (ie:steam, gog, origin installs)

    walks directories, looking for tool.doot.data.raw.key files

    origin: looks for __Installer/installerdata.xml
    steam: looks for appmanifest_*.acf, gets {name, installdir, SizeOnDisk}, uses common/{installdir}/
    misc: specific exe's ["Viva Pinata.exe"...]

    creates a listing of each game directory
    """
    pass
