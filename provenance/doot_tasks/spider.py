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

import doot
from doot import globber, tasker
from doot.mixins.importer import ImporterMixin
from doot.mixins.toml_reader import TomlReaderMixin
from doot.mixins.spider import SpiderMixin
from provenance.mixins.dataset_globber import CADatasetGlobber

class DataCrawl(CADatasetGlobber):
    """
    Scraper for raw directories (ie:steam, gog, origin installs)

    walks directories, looking for tool.doot.data.raw.key files

    origin: looks for __Installer/installerdata.xml
    steam: looks for appmanifest_*.acf, gets {name, installdir, SizeOnDisk}, uses common/{installdir}/
    misc: specific exe's ["Viva Pinata.exe"...]

    creates a listing of each game directory
    """
    pass


class RunSpider(SpiderMixin, CADatasetGlobber, ImporterMixin, TomlReaderMixin):
    """
    Run a spider from a zip marker toml,
    spider class is set in dataset.crawl.spider
    spider settings defined in dataset.crawl.settings

    """

    def __init__(self, name="spider::data", locs=None, roots=None):
        super().__init__(name, locs, roots=roots or [locs.data])
        self.current_spider = None
        self.data_dir       = None
        self.select_tags.append("spider")

    def subtask_detail(self, task, fpath):
        data = self.read_toml(fpath / self.dataset_marker)
        if not data.on_fail(False).dataset.crawl():
            # Not a spider dataset
            return None
        spider_cls      = self.import_class(data.dataset.crawl.spider)
        spider_settings = dict(data.flatten_on().dataset.crawl.settings())

        task.update({
            "actions": [
                (self.set_data_dir, [fpath]),
                (self.run_spider, [
                    data.dataset.instance.name,
                    spider_cls,
                    data.dataset.instance.source,
                ],
                 {
                     "settings": spider_settings,
                     "auto_limit" : True,
                 }
                 )
            ]
        })
        return task


    def set_data_dir(self, fpath):
        self.data_dir = self.to_mirro(fpath, "crawl")
