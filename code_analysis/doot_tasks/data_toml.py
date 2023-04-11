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
from doot import tasker
from doot.tasks.files.backup import BackupTask

from doot.mixins.batch import BatchMixin
from code_analysis.mixins.dataset_globber import CADatasetGlobber

dataset_marker = doot.config.on_fail(".zipthis.toml", str).dataset.marker()

class TomlSummary(CADatasetGlobber, BatchMixin):

    """
    Find all zip markers, and add the basic toml structure for them
    """

    def __init__(self, name="toml::summarise", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)

    def filter(self, fpath):
        zip_f = fpath / self.dataset_marker
        if fpath.is_dir() and zip_f.exists():
            if zip_f.stat().st_size == 0:
                logging.info(f"Found Empty Toml: {fpath}")
                return self.globc.yes
            else:
                logging.info(f"Toml Has Content, skipping: {fpath}")

        return self.globc.no

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [
                (self.prepare_toml, [fpath]),
            ]
        })
        return task

    def prepare_toml(self, fpath):
        logging.info(f"Preparing Dataset Toml: {fpath}")
        existing_text : str           = (fpath / self.dataset_marker).read_text().strip()
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
        (fpath / self.dataset_marker).write_text(text)

    def verify_toml(self, text):
        # TODO
        pass

class TomlConcat(tasker.DootTasker):
    """
    Combine all dataset_markers
    """

    def __init__(self, name="toml::concat", locs=None):
        super().__init__(name, locs)
        self.output = locs.build / "datasets.toml"

    def task_detail(self, task):
        task.update({
            "actions" : [ self.append_all_dataset_summaries ],
        })
        return task

    def append_all_dataset_summaries(self):
        globbed = list(self.locs.data.rglob(dataset_marker))
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

    def __init__(self, name="toml::adjust", locs=None, processor=None):
        super().__init__(name, locs)
        self.dataset_re = re.compile(r"^\[dataset\]")
        self.listing_re = re.compile(r"^listing\s+=\s+(\[.+?\])")
        self.hash_re    = re.compile(r"^data-zip-hash")
        self.processor  = processor

    def filter(self, fpath):
        if fpath.name == dataset_marker:
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
        globbed = list(self.locs.data.rglob(dataset_marker))
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
    """
    List the datasets, sorted by last modification time
    """

    def __init__(self, name="toml::age", locs=None):
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
        self.data = list(self.locs.data.rglob(dataset_marker))

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
    """
    List datasets that aren't tagged
    """

    def __init__(self, name="toml::tagless", locs=None):
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
        self.globbed = list(self.locs.data.rglob(dataset_marker))

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
