#!/usr/bin/env python3
"""

"""
##-- imports
from __future__ import annotations

import abc
import logging as logmod
import pathlib as pl
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from re import Pattern
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable)
from uuid import UUID, uuid1
from weakref import ref

if TYPE_CHECKING:
    # tc only imports
    pass
##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
# If CLI:
# logging = logmod.root
# logging.setLevel(logmod.NOTSET)
##-- end logging

import doot
from doot import globber

class BasicSummary(globber.DirGlobber):
    """
    Report the contents of each dir
    number of files, line counts, extensions etc
    """

    def __init__(self, name="summary::basic", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task

class BasicGrep(globber.EagerFileGlobber):
    """
    naive grepping through files for specific patterns
    """

    def __init__(self, name="grep::basic", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class CSVSummary(globber.EagerFileGlobber):
    """
    Get columns, row counts
    """

    def __init__(self, name="summary::csv", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [".csv"])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class GrammarSummary(globber.EagerFileGlobber):
    """
    Report on grammar sizes, nodes, leaves, roots, variants
    """

    def __init__(self, name="summary:grammars", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class XMLElementSummary(globber.DirGlobber):
    """
    extract xml element structures
    """

    def __init__(self, name="summary::xml.elements", locs=None, roots=None, rec=True, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task

class SpreadsheetSummary(globber.EagerFileGlobber):
    """

    """

    def __init__(self, name="summary::spreadsheet", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class NYTSummary(globber.EagerFileGlobber):
    """
    Summarise nyt json data
    """

    def __init__(self, name="summary::nyt", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [".json"])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class FictionSummary(globber.EagerFileGlobber):
    """

    """

    def __init__(self, name="summary::fiction", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def filter(self, fpath):
        return self.control.accept

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task
