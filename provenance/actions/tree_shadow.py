#!/usr/bin/env python3
"""
TODO
  Tree shadowing separates transforms of data into similarly structured directoy trees,
  while symlinking their provenance.toml metadata,
  and copying+appending to the transforms.toml to record how to make this tree set

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


class ShadowData:
    """ Shadow an Existing Dataset as {name},
      symlink the provenance toml, copy the transform log
      """
    pass

class ShadowAddTransform:
    """ Add a transform to the task log for this shadow """
    pass

class ShadowMask:
    """ Add a file mask for this shadow tree to subselect files """
    pass



"""


"""
