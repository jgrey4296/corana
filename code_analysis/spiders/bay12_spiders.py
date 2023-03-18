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

from doot.spiders.spiders import DootBasicSpider

class DevLogSpider(DootBasicSpider):

    def parse(self, response):
        yield from response.follow_all(xpath="//p/a/@href[contains(self::node(), 'dwarves/dev')]", callback=self.parse_bay12)

        for dev_entry in response.css(".dev_progress").getall():
            yield {
                "source_url"     : response.url,
                "data"           : dev_entry,
                "needs_subsplit" : False,
            }
