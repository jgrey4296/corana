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

printer = logmod.getLogger("doot._printer")

import tomlguard
import doot
import doot.errors
from doot.structs import DootKey
from doot.mixins.action.human_numbers import HumanMixn

from_k     = DootKey.make("from")
update_k   = DootKey.make("update_")
focus_k    = DootKey.make("focus_keys")
merge_k    = DootKey.make("merge_keys")

# https://developers.google.com/youtube/v3/docs/videos

focus_keys           = [
                     "fulltitle", "title", "description", "duration_string", "view_count", "webpage_url", "automatic_captions.en",
                     "chapters", "upload_date", "playlist", "playlist_id", "playlist_title", "was_live", "epoch", "language",
                     "like_count", "comment_count", "view_count", "chapters"
]
merge_keys           = ["tags", "categories"]

def reduce_video_metadata(spec, state):
    update = update_k.redirect(spec)
    json  = tomlguard.TomlGuard(from_k.to_type(spec, state, type_=dict))
    keys  = set(json.keys())
    focus = set(focus_k.to_type(spec, state, type_=list))
    merge = set(merge_k.to_type(spec, state, type_=list))
    printer.info("Json has matching: %s", focus & keys)

    reduced = {}
    date = datetime.datetime.strptime(data.upload_date, "%Y%m%d")
    fsize = HumanMixin.human_sizes(data.filesize_approx)

    for key in focus & keys:
        reduced[key] = json[key]

   return { update : reduced }
