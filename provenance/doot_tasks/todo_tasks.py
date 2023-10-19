#!/usr/bin/env python3
"""
Tasks for generating code, such as XML and Json interfaces

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
##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

import doot
from provenance.mixins.dataset_globber import CADatasetGlobber

class XMLElementSummary(CADatasetGlobber):
    """
    extract xml element structures
    """

    def __init__(self, name="summary::xml.elements", locs=None, roots=None, rec=True, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task

class DialogTreeSummary(CADatasetGlobber):
    """
    summarise dialog tree characteristics
    """

    def __init__(self, name="summary::dialog", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task


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
        return task

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

class RunGrammar(CADatasetGlobber):
    """
    load and run a (tracery) grammar, printing the result,
    and saving it into a grammar log
    """

    def __init__(self, name="grammar::run", locs=None):
        super().__init__(name, locs)
        self.output                 = self.locs.build
        self.current_grammar : dict = {}

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

class ApplyParser(CADatasetGlobber):
    """
    (data -> temp) Apply a parser to all files globbed to create itermediate representations
    """
    def __init__(self, name="", locs=None, roots=None, rec=False, exts=None, parser=None):
        super().__init__(name, locs, roots or [locs.], rec=rec, exts=exts or [])
        self.parser = parser

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class ParseReport(CADatasetGlobber):
    """
    Give reports for all parsed files for a certain type
    """
    def __init__(self, name="parser::report", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.temp], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class PatchExtraction(CADatasetGlobber):
    """
    Extract data from patch notes
    """
    def __init__(self, name="patch::extract", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class ObsidianPass(CADatasetGlobber):
    """
    Prep obsidian files for use.
    rename conversation, stringtable and quest structure files to xml
    """
    pass

class WikiDownload(CADatasetGlobber):
    """
    Download raw html from game wiki's
    and extract the core data part
    """
    pass

class RepoClone(CADatasetGlobber):
    """
    Clone Certain github repo's for data
    """
    pass

class DwarfBugs(CADatasetGlobber):
    """
    Get the dwarf fortress buglist from:
    https://www.bay12games.com/dwarves/mantisbt/view_all_bug_page.php
    """
    pass

class QuestExtract(CADatasetGlobber):
    """
    Extract data from quest descriptions
    """
    def __init__(self, name="quest::extract", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class RuleDescriptions(CADatasetGlobber):
    """
    describe rule characteristics. size of pre/post conditions etc
    """
    def __init__(self, name="rules::extract", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class BasicSummary(CADatasetGlobber):
    """
    Report the contents of each dir
    number of files, line counts, extensions etc
    """

    def __init__(self, name="summary::basic", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [],
        })
        return task

class BasicGrep(CADatasetGlobber):
    """
    naive grepping through files for specific patterns
    """

    def __init__(self, name="grep::basic", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class CSVSummary(CADatasetGlobber):
    """
    Get columns, row counts
    """

    def __init__(self, name="summary::csv", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [".csv"])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class GrammarSummary(CADatasetGlobber):
    """
    Report on grammar sizes, nodes, leaves, roots, variants
    """

    def __init__(self, name="summary:grammars", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class SpreadsheetSummary(CADatasetGlobber):
    """

    """

    def __init__(self, name="summary::spreadsheet", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class NYTSummary(CADatasetGlobber):
    """
    Summarise nyt json data
    """

    def __init__(self, name="summary::nyt", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [".json"])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class FictionSummary(CADatasetGlobber):
    """

    """

    def __init__(self, name="summary::fiction", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.data], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task

class BuildVisuals(CADatasetGlobber):
    """
    Build latex/plantuml/sankey/graph/chart visuals from descriptions
    """
    def __init__(self, name="visuals::build", locs=None, roots=None, rec=False, exts=None):
        super().__init__(name, locs, roots or [locs.temp], rec=rec, exts=exts or [])

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : []
        })
        return task
