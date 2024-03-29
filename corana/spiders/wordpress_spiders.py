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
from scrapy.http.response.xml import XmlResponse

class WordpressSpider(DootBasicSpider):

    def parse(self, response):
        assert(isinstance(response, XmlResponse))
        response.selector.remove_namespaces()
        yield from response.follow_all(xpath="//loc/text()", callback=self.parse_wordpress_post)

    def parse_wordpress_post(self, response):
        yield {
            "source_url"     : response.url,
            "data"           : response.css(".post"),
            "needs_subsplit" : True,
        }
