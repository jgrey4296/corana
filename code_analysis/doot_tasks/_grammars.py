#!/usr/bin/env python3
"""

"""
##-- imports

##-- end imports

##-- default imports
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

##-- end default imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

import doot
from doot import tasker, globber

class RunGrammar(tasker.DootTasker):
    """
    load and run a (tracery) grammar, printing the result,
    and saving it into a grammar log
    """

    def __init__(self, name="grammar::run", locs=None):
        super().__init__(name, locs)
        self.output                 = self.locs.build
        self.current_grammar : dict = {}

    def set_params(self):
        return [

        ]

    def task_detail(self, task):
        task.update({
            "actions": [self.load_grammar,
                        self.run_grammar,
                        self.report_result,
                     ],
        })
        return task

    def load_grammar(self):
        target = (self.locs.tracery / self.args['grammar']).with_suffix(".json")
        self.current_grammar = json.loads(target.read_text())

    def run_grammar(self):
        # loop

        return { "result" : None }

    def report_result(self, task):
        grammar_name = pl.path(self.args['grammar']).stem.replace(" ","_")
        out_log_name = self.output / f"grammar_{grammar_name}.log"
        with open(out_log_name, 'a') as f:
            f.write("\n" + task.values['result'])

        print(f"Result: {task.values['result']}")

class GrammarReport(globber.DootEagerGlobber):
    """
    Report on the sizes of all grammars
    """

    def __init__(self, name="grammar::report", locs=None, roots=None, exts=None, rec=False):
        super().__init__(name, locs, roots or [locs.tracery], rec=rec, exts=exts or [".json"])
        self.output = self.locs.build / "tracery.report"

    def task_detail(self, task):
        task.update({
            "targets": [self.output],
            "clean" : True,
        })
        return tas
    def subtask_detail(self, task, fpath):
        task.update({
            "actions": [
                (self.load_grammar, [fpath]),
                self.summarise,
                self.report,
            ],
        })
        return task

    def load_grammar(self, fpath):
        self.current_grammar = json.loads(fpath.read_text())

    def summarise(self):
        with open(self.output, 'a') as f:
            pass
