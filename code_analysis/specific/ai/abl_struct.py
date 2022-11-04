#!/usr/bin/env python3
##-- imports
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic
from dataclasses import dataclass, field, InitVar

from enum import Enum

from code_analysis.util.parse_base import ParseBase

##-- end imports

ABL_E = Enum('ABL_E', 'ENT ACT WME CONFLICT BEH COM SPAWN MENTAL PRECON SPEC INIT STEP COMMENT PRIORITY SUCCTEST SPAWNTARGET')
obj_e = ABL_E

enum_to_str = {
    obj_e.ENT      : "entity",
    obj_e.ACT      : "act",
    obj_e.WME      : "wme",
    obj_e.CONFLICT : "conflict",
    obj_e.BEH      : "behaviour",
    obj_e.COM      : "com",
    obj_e.SPAWN    : "spawngoal",
    obj_e.MENTAL   : "mental_act",
    obj_e.PRECON   : "precondition",
    obj_e.SPEC     : "specificity",
    obj_e.INIT     : "init",
    obj_e.STEP     : "step",
    obj_e.COMMENT  : "comment",
    obj_e.PRIORITY : "priority",
    obj_e.SUCCTEST : "success_test",
    obj_e.SPAWNTARGET : "spawn at"
}


@dataclass
class AblEnt(ParseBase):

    def __post_init__(self):
        self.type = obj_e.ENT

    def to_dict(self):
        obj = super().to_dict()
        obj['type'] = enum_to_str[self.type]
        return obj

@dataclass
class AblRegistration(ParseBase):

    def __post_init__(self):
        assert(self.type in [obj_e.WME, obj_e.ACT, obj_e.CONFLICT])

    def to_dict(self):
        obj = super().to_dict()
        obj['type'] = enum_to_str[self.type]
        return obj


@dataclass
class AblBehavior(ParseBase):

    def __post_init__(self):
        self.type = obj_e.BEH

    def to_dict(self):
        obj = super().to_dict()
        obj['type'] = enum_to_str[self.type]
        return obj

@dataclass
class AblComponent(ParseBase):

    def __post_init__(self):
        assert(self.type in [obj_e.SPAWN,
                          obj_e.MENTAL,
                          obj_e.PRECON,
                          obj_e.SPEC,
                          obj_e.STEP,
                          obj_e.PRIORITY,
                          obj_e.SUCCTEST]), self.type

    def to_dict(self):
        _type = enum_to_str[self.type]

        base_dict = super().to_dict()
        base_dict["type"] = _type
        if self.name is None:
            base_dict["name"] = "Anon"

        return base_dict

@dataclass
class AblMisc(ParseBase):
    pass
