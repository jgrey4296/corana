#/usr/bin/env python3
"""

"""
##-- imports
from __future__ import annotations

import abc
import logging as logmod
import pathlib as pl
from enum import Enum, auto
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from re import Pattern
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable)
from uuid import UUID, uuid1
from weakref import ref

if TYPE_CHECKING:
    # tc only imports
    pass
##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

##-- enums
class ExtractTypeEnum:
    single_file = auto()
    directory   = auto()
    part_of_file = auto()

class PDDLTypeEnum:
    domain  = auto()
    problem = auto()

##-- end enums


@dataclass
class DataExtractBase:
    """
    Base for all forms of data extracted from code.
    records the source of the data,
    the extensions of file types used
    and whether its an entire directory or a single file
    """
    source      : pl.Path         = field()
    raw_size    : int             = field()
    exts        : set[str]        = field(kw_only=True, default_factory=set)
    source_type : ExtractTypeEnum = field(kw_only=True, default=ExtractTypeEnum.single_file )




##-- grammar
@dataclass
class GrammarData(DataExtractBase):
    """
    For holding information about grammars. eg: tracery
    """
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    num_keys : int      = field()
    key_set  : set[str] = field(default_factory=set)


    avg_val_count         : float    = field(init=False)
    avg_val_len           : float    = field(init=False)
    max_depth_from_origin : int      = field(init=False)
    isolated_keys         : set[str] = field(init=False)
    uses_emojis           : bool     = field(init=False)
    uses_svg              : bool     = field(init=False)
    uses_links            : bool     = field(init=False)



##-- end grammar

##-- rule ai
@dataclass
class AgentSpeakData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.part_of_file)
    imports     : set[str]
    plan_name   : str
    actions     : dict[str, list[str]]
    beliefs     : dict[str, list[str]]
    tests       : dict[str, list[str]]
    variables   : dict[str, set[str]]

@dataclass
class CLIPSData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    modules    : set[str]
    defglobals : set[str]
    rules      : dict[str, tuple[int, int]]
    functions  : set[str]
    templates  : dict[str, set[str]]

@dataclass
class CifData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    name : str
    # game | story
    cif_type : str
    # type -> count
    rules : dict[str, int]
    predicate_types : set[str]
    effects : int

    dialogue : int




##-- end rule ai
##-- mas
@dataclass
class JacamoData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    mas          : str
    agents       : set[str]
    # agent -> [goals]
    goals        : dict[str, set[str]]
    # agent -> [files]
    bases        : dict[str, set[str]]
    # org -> [spec/assignments]
    orgs         : dict[str, set[str]]
    assignments  : dict[str, str]
    platforms    : set[str]

@dataclass
class MAS2JData(DataExtractBase):
    source_type    : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    mas            : str
    agents         : set[str]
    infrastructure : str


@dataclass
class MoiseData(DataExtractBase):
    source_type       : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    org_name          : str
    # role -> extends
    roles             : dict[str, set[str]]
    # group -> roles/links
    group_roles       : dict[str, set[str]]
    group_links       : dict[str, set[Any]]
    group_constraints : dict[str, set[Any]]

    # scheme -> goals/mission
    scheme_goals    : dict[str, Any]
    scheme_missions : dict[str, Any]

    # normType : [ definition ]
    norms             : dict[str, set[Any]]

@dataclass
class CPlusData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)

    imports        : set[str]
    objects        : set[str]
    sorts          : set[str]
    queries        : set[str]
    variables      : set[str]
    constants      : set[str]
    macros         : set[str]
    constraints    : set[str]
    causes         : set[str]
    nonexecutables : set[str]
    defaults       : set[str]
    inertials      : set[str]



##-- end mas
##-- plans
@dataclass
class PDDLData(DataExtractBase):
    source_type   : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    name          : str
    pddl_type     : PDDLTypeEnum
    predicates    : set[str]
    actions       : set[str]
    effects       : set[str]
    inits         : set[str]
    defined_types : dict[str, set[str]]
    goals         : set[str]


##-- end plans

##-- source code



@dataclass
class InstalData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.part_of_file)
    institution     : str
    types           : set[str]
    external_events : set[str]
    inst_events     : set[str]
    violations      : set[str]
    inertials       : set[str]
    obligations     : set[str]
    transients      : set[str]
    initials        : int
    gen_rules       : int
    terminate_rules : int
    initiate_rules  : int
    transient_rules : int


@dataclass
class ABLData(DataExtractBase):
    """
    Data extracted from ABL
    """
    source_type      : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    entities         : set[str]
    conflicts        : dict[str, set[str]]
    wmes             : set[str]
    acts             : set[str]
    seq_behaviours   : set[str]
    joint_behaviours : set[str]


@dataclass
class VersuData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    # name signature and length
    funcs           : set[str, int]
    # if X's
    tests           : set[str]
    calls           : set[str]
    # Basetype -> [subtypes]
    types           : dict[str, set[str]]
    inserts         : set[str]
    deletes         : set[str]
    raw_strs        : set[str]
    # length -> count
    sentence_counts : dict[int, int]
    imports         : set[str]
    # name -> type
    variables       : dict[str, str]


@dataclass
class SoarData(DataExtractBase):
    source_type : ExtractTypeEnum = field(default=ExtractTypeEnum.single_file)
    productions : set[str]
    # prod -> count
    conditions  : dict[str, int]
    actions     : dict[str, int]
    bindings    : dict[str, set[str]]


@dataclass
class CSharpData(DataExtractBase):
    pass

@dataclass
class LuaData(DataExtractBase):
    pass

@dataclass
class WitcherScriptData(DataExtractBase):
    pass

@dataclass
class ParadoxScriptData(DataExtractBase):
    pass

##-- end source code

##-- dialog
@dataclass
class DialogTree(DataExtractBase):
    pass

##-- end dialog

##-- fiction
@dataclass
class FictionData(DataExtractBase):
    pass

##-- end fiction

##-- names
@dataclass
class NameData(DataExtractBase):
    pass
##-- end names

##-- quests
@dataclass
class QuestData(DataExtractBase):
    pass



##-- end quests

##-- simulation
@dataclass
class SimulationData(DataExtractBase):
    pass

@dataclass
class BugsData(DataExtractBase):
    pass

##-- end simulation

##-- patches
@dataclass
class PatchData(DataExtractBase):
    pass

@dataclass
class DevLog(DataExtractBase):
    pass

##-- end patches
