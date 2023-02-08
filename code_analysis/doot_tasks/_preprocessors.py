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

class WeiduPass(tasker.DootTasker):
    """
    Run Weidu, the infinity engine dialog decompiler,
    to extract all available dialogs
    """
    pass

class ObsidianPass(tasker.DootTasker):
    """
    Prep obsidian files for use.
    rename conversation, stringtable and quest structure files to xml
    """
    pass

class WikiDownload(tasker.DootTasker):
    """
    Download raw html from game wiki's
    and extract the core data part
    """
    pass

class RepoClone(tasker.DootTasker):
    """
    Clone Certain github repo's for data
    """
    pass

class DwarfBugs(tasker.DootTasker):
    """
    Get the dwarf fortress buglist from:
    https://www.bay12games.com/dwarves/mantisbt/view_all_bug_page.php
    """
    pass
