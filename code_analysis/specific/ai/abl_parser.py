#!/usr/bin/env python
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import pyparsing as pp

from code_analysis.util.parse_base import ParseBase

import abl_struct as ABS
obj_e = ABS.ABL_E

s               = pp.Suppress
op              = pp.Optional
lineEnd         = pp.lineEnd
NAME            = pp.Word(pp.alphanums + "_")
NUM             = pp.Word(pp.nums + ".")
SEMICOLON       = pp.Literal(";")
O_BRACKET       = pp.Literal('{')
C_BRACKET       = pp.Literal('}')

act_abl         = pp.Keyword("act")
atomic_abl      = pp.Keyword("atomic")
be_abl          = pp.Keyword("behaving_entity")
behavior_abl    = pp.Keyword("behavior")
fail_abl        = pp.Keyword("fail_step")
joint_abl       = pp.Keyword("joint")
mental_abl      = pp.Keyword("mental_act")
parallel_abl    = pp.Keyword("parallel")
precond_abl     = pp.Keyword("precondition")
register_abl    = pp.Keyword("register")
sequential_abl  = pp.Keyword("sequential")
spawn_abl       = pp.Keyword("spawngoal")
specificity_abl = pp.Keyword("specificity")
subgoal_abl     = pp.Keyword("subgoal")
wme_abl         = pp.Keyword("wme")
initial_abl     = pp.Keyword("initial_tree")
succeed_abl     = pp.Keyword("succeed_step")
fail_abl        = pp.Keyword("fail_step")
conflict_abl    = pp.Keyword('conflict')
import_abl      = pp.Keyword('import')


with_abl         = pp.Keyword("with")
priority_abl     = pp.Keyword('priority')
persistent_abl   = pp.Keyword('persistent')
success_test_abl = pp.Keyword('success_test')
ignore_failure_abl = pp.Keyword('ignore_failure')
teammembers_abl    = pp.Keyword('teammembers')

parallel_abl.setParseAction(lambda x: "Parallel")
sequential_abl.setParseAction(lambda x: "Sequential")


def build_parser():
    """ Build a rough parser for abl """

    beh_ent_stmt      = s(be_abl) + NAME
    register_act_stmt = s(register_abl + act_abl) + NAME
    register_wme_stmt = s(register_abl + wme_abl) + NAME

    behavior_stmt = (op(atomic_abl) + op(joint_abl)).setResultsName("args") + \
                     pp.Or([sequential_abl, parallel_abl]).setResultsName('form') + \
                     s(behavior_abl) + pp.Group(NAME).setResultsName("name")

    spawn_stmt        = pp.Or([spawn_abl, subgoal_abl, act_abl]) + NAME
    skip_to_spawn     = s(pp.SkipTo(spawn_stmt)) + spawn_stmt
    step_stmt         = pp.Or([succeed_abl, fail_abl])
    skip_to_step      = s(pp.SkipTo(step_stmt)) + step_stmt
    mental_stmt       = mental_abl
    precondition_stmt = precond_abl
    spec_stmt         = s(specificity_abl) + NUM
    conflict_stmt     = s(conflict_abl) + NAME + NAME
    import_stmt       = s(import_abl) + pp.restOfLine

    # TODO add wme definition
    # TODO add with statements

    # Parse Actions
    beh_ent_stmt.setParseAction(      lambda x: ABS.AblEnt(x[0]))

    register_act_stmt.setParseAction( lambda x: ABS.AblRegistration(x[0], obj_e.ACT))
    register_wme_stmt.setParseAction( lambda x: ABS.AblRegistration(x[0], obj_e.WME))
    conflict_stmt.setParseAction(     lambda x: ABS.AblRegistration(x[:], obj_e.CONFLICT))

    behavior_stmt.setParseAction(     lambda x: ABS.AblBehavior(x['name'][0],
                                                           args=x['args'][:] + [x['form']]))

    spawn_stmt.setParseAction(        lambda x: ABS.AblComponent(x[1], obj_e.SPAWN,
                                                            args=[x[0]]))
    step_stmt.setParseAction(         lambda x: ABS.AblComponent(x[0], obj_e.STEP))
    mental_stmt.setParseAction(       lambda x: ABS.AblComponent(type=obj_e.MENTAL))
    precondition_stmt.setParseAction( lambda x: ABS.AblComponent(type=obj_e.PRECON))
    spec_stmt.setParseAction(         lambda x: ABS.AblComponent(type=obj_e.SPEC,
                                                            args=[float(x[0])]))

    initial_abl.setParseAction(       lambda x: ABS.AblBehavior("initial_tree"))
    import_stmt.setParseAction(       lambda x: ABS.AblMisc('import', args=[x[:]]))

    pass_stmt = pp.restOfLine
    pass_stmt.setParseAction(lambda x: ParseBase('Pass'))

    com_parser = pp.dblSlashComment
    com_parser.setParseAction(lambda x: obj_e.COMMENT)

    abl_parser = pp.MatchFirst([com_parser,
                                import_stmt,
                                beh_ent_stmt,
                                register_act_stmt,
                                register_wme_stmt,
                                conflict_stmt,
                                behavior_stmt,
                                skip_to_spawn,
                                skip_to_step,
                                mental_stmt,
                                precondition_stmt,
                                spec_stmt,
                                pass_stmt])

    return abl_parser
