#!/usr/bin/env python3
"""

"""
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
printer = logmod.getLogger("doot._printer")
##-- end logging

from collections import defaultdict
import tomlguard
import doot
from doot._abstract import Command_i
from doot.structs import TaskStub, DootTaskName

from corana.mixins.marker_manip import MarkerManipulationMixin

class CoranaMetaDataCmd(Command_i):
    """
      For modifying corana metadata from the command line
    """
    _name      = "prov"
    _help      = [ "Corana Metadata Editing" ]

    @property
    def param_specs(self) -> list:
        return super().param_specs + []

    def __call__(self, tasks:TomlGuard, plugins:TomlGuard):
        printer.info("This is an Example Cmd edited")


class CoranaMetaStubCmd(Command_i, MarkerManipulationMixin):
    """
      For modifying corana metadata from the command line
    """
    _name      = "prov-stub"
    _help      = [ "Corana Metadata Marker File Stub generation" ]

    @property
    def param_specs(self) -> list:
        return super().param_specs + [
            self.make_param("target", type=str,          default="", positional=True),
            self.make_param("suppress-header",           default=True, invisible=True)
            ]

    def __call__(self, tasks:TomlGuard, plugins:TomlGuard):
        """
        This creates a toml stub using default values, as best it can
        """
        printer.info("Generating Stub Corana Toml")
        target                     = pl.Path(doot.args.cmd.args.target)
        match self.make_marker(target):
            case False:
                return False
            case { "marker": fpath }:
                printer.info("Stub Generated in: %s", fpath)
                # TODO stub a .corana directory



class CoranaMetaPrintCmd(Command_i, MarkerManipulationMixin):
    """
      For modifying corana metadata from the command line
    """
    _name      = "prov-print"
    _help      = [ "Corana Metadata Marker File Stub generation" ]

    @property
    def param_specs(self) -> list:
        return super().param_specs + [
            self.make_param("target", type=str,          default="", positional=True),
            self.make_param("suppress-header",           default=True, invisible=True)
            ]

    def __call__(self, tasks:TomlGuard, plugins:TomlGuard):
        """
        This creates a toml stub using default values, as best it can
        """
        printer.info("Generating Stub Corana Toml")
        target                     = pl.Path(doot.args.cmd.args.target)
        match self.find_marker(target):
            case None:
                printer.warning("No Corana Metadata found in target or it's parents: %s", target)
                return False
            case pl.Path() as marker:
                loaded = tomlguard.load(marker)
                text = marker.read_text()

                printer.info("-- Dataset: %s", loaded.dataset.instance.name)
                printer.info(text)
