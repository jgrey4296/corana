#!/usr/bin/env python3
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic
from dataclasses import dataclass, field, InitVar

from enum import Enum

from code_analysis.util.parse_base import ParseBase

ABL_E = Enum('ABL_E', 'ENT ACT WME CONFLICT BEH COM SPAWN MENTAL PRECON SPEC INIT STEP COMMENT')
obj_e = ABL_E

@dataclass
class AblEnt(ParseBase):

    def __post_init__(self):
        self.type = obj_e.ENT


@dataclass
class AblRegistration(ParseBase):

    def __post_init__(self):
        assert(self.type in [obj_e.WME, obj_e.ACT, obj_e.CONFLICT])


@dataclass
class AblBehavior(ParseBase):

    def __post_init__(self, init=False):
        self.type = obj_e.BEH
        self.init = init

    def add_component(self, comp):
        self.components.append(comp)


@dataclass
class AblComponent(ParseBase):

    def __post_init__(self):
        assert(self.type in [obj_e.SPAWN,
                             obj_e.MENTAL,
                             obj_e.PRECON,
                             obj_e.SPEC,
                             obj_e.STEP])

    def to_dict(self):
        _type = ""
        if self.type == obj_e.MENTAL:
            _type = "MentalAct"
        elif self.type == obj_e.PRECON:
            _type = "Precondition"
        elif self.type == obj_e.STEP:
            _type = "Step"
        elif self.type == obj_e.SPEC:
            _type = "Specificity"
        elif self.type == obj_e.SPAWN and 'subgoal' in self.args:
            _type = "SubGoal"
        elif self.type == obj_e.SPAWN and 'act' in self.args:
            _type = "Act"
        else:
            _type = "SpawnGoal"

        name = ""
        if self.name is not None:
            name = "{}".format(self.name)

        args = [str(x) for x in self.args if x not in ["act", "spawngoal", "subgoal"]]

        return { 'type' : _type, 'name': name, 'args': args }



@dataclass
class AblMisc(ParseBase):
    pass
