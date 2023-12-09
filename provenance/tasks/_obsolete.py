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

class WeiduUnpack(globber.LazyGlobMixin, globber.DirGlobMixin, globber.EagerFileGlobber, task_mixins.TargetedMixin):
    """
    Processing Infinity engine BIFF files using weidu
    """

    def __init__(self, name="weidu::biffs", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True):
        self.game_dir : pl.Path = None
        self.output : pl.Path   = None

    def filter(self, fpath):
        if (fpath / "chitin.key").exists():
            return self.control.keep
        return self.control.discard

    def task_detail(self, task):
        task.update({
            "actions": [],
        })
        return task

    def enumerate_all_biffs(self):
        self.cmd(weidu_exec, "--game", self.game_dir,
                 "--list-biffs", "--out", self.output / "biff.listing")

        self.cmd(weidu_exec, "--game", self.game_dir,
                 "--list-files", "--out", self.output / "resources.listing")

    def enumerate_biff(self, fpath):
        rel_fpath = fpath.relative_to(self.game_dir)

        self.cmd(weidu_exec, "--game", self.game_dir,
                 "--biff", rel_fpath,
                 "--out", self.output / f"{fpath.stem}.listing")

    def extract_resource(self, *fpaths):
        targets = list(fpaths)
        args = [val for pair in zip(["--biff-get"]*len(targets),
                                    targets) for val in pair]

        self.cmd(weidu_exec, "--game", self.game_dir,
                 *args
                 "--out", self.output)


    def decompile_dlg(self, fpath):
        self.cmd(weidu_exec, "__game", self.game_dir,
                 "--use-lang", game_lang,
                 *weidu_d_opts,
                 fpath,
                 "--out", self.output)
