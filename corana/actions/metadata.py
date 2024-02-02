#!/usr/bin/env python3
"""


See EOF for license/metadata/notes as applicable
"""

##-- builtin imports
from __future__ import annotations

# import abc
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
import types
import weakref
# from copy import deepcopy
# from dataclasses import InitVar, dataclass, field
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable, Generator)
from uuid import UUID, uuid1

##-- end builtin imports

##-- lib imports
import more_itertools as mitz
##-- end lib imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

import shutil
import doot
import doot.errors
from doot.structs import DootKey

from corana.constants import METADATA_DIRECTORY_NAME, METADATA_DIRECTORY_CONTENTS

from_key   = DootKey("from")
target_key = DootKey("target")

def verify_corana_files(spec, state):
    raise NotImplementedError("TODO")

def build_corana_directory(spec, state):
    target = target_key.to_path(spec, state)
    meta_dir = target / METADATA_DIRECTORY_NAME
    if not target.is_dir() or meta_dir.exists():
        raise doot.errors.DootTaskError("Metadata directory already exists")

    meta_dir.mkdir()
    for fname in METADATA_DIRECTORY_CONTENTS:
        (meta_dir / fname).touch()

def copy_corana_directory(spec, state):
    source = from_key.to_path(spec, state)
    target = target_key.to_path(spec, state)
    source_meta_dir = target / METADATA_DIRECTORY_NAME
    target_meta_dir = target / METADATA_DIRECTORY_NAME
    if not source.is_dir() or not source_meta_dir.exists():
        raise doot.errors.DootTaskError("Metadata directory not found in source")

    if not target.is_dir() or target_meta_dir.exists():
        raise doot.errors.DootTaskError("Metadata directory already exists")

    target_meta_dir.mkdir()
    for fname in METADATA_DIRECTORY_CONTENTS:
        shutil.copy(source_meta_dir / fname, target_meta_dir / fname)
        match fname:
            case "files.jsonl":
                pass
            case "history.jsonl":
                pass
            case "tasks.toml":
                pass
            case "environment.toml":
                pass
            case "notes.txt" | "readme.txt":
                pass


    # load source / METADATA_FILE_NAME
    # increment distance_from_raw_data by 1
    # Write to target / METADATA_FILE_NAME
    raise NotImplementedError("TODO")
