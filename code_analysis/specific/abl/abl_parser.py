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
SEMICOLON       = s(pp.Literal(";"))
O_BRACKET       = s(pp.Literal('{'))
C_BRACKET       = s(pp.Literal('}'))
O_PAR           = s(pp.Literal('('))
C_PAR           = s(pp.Literal(')'))
EQUAL           = s(pp.Literal('='))

act_abl         = pp.Keyword("act")
atomic_abl      = pp.Keyword("atomic")
be_abl          = pp.Keyword("behaving_entity")
behavior_abl    = pp.Keyword("behavior")
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
wait_abl        = pp.Keyword('wait')


with_abl           = pp.Keyword("with")
priority_abl       = pp.Keyword('priority')
persistent_abl     = pp.Keyword('persistent')
success_test_abl   = pp.Keyword('success_test')
ignore_failure_abl = pp.Keyword('ignore_failure')
teammembers_abl    = pp.Keyword('teammembers')

parallel_abl.setParseAction(lambda x: "Parallel")
sequential_abl.setParseAction(lambda x: "Sequential")

def build_with_stmt(results):
    target = results.target
    args   = results.head[:]
    target.args += args
    return target

def build_parser():
    """ Build a rough parser for abl """
    return build_single_line_parser(), build_multi_line_parser()

def build_single_line_parser():
    beh_ent_stmt      = s(be_abl) + NAME
    register_act_stmt = s(register_abl + act_abl) + NAME + with_abl + NAME
    register_wme_stmt = s(register_abl + wme_abl) + NAME + with_abl + NAME
    conflict_stmt     = s(conflict_abl) + NAME + pp.OneOrMore(NAME)
    import_stmt       = s(import_abl) + pp.restOfLine

    behavior_stmt = (op(atomic_abl) + op(joint_abl)).setResultsName("args") + \
                     pp.Or([sequential_abl, parallel_abl]).setResultsName('form') + \
                     s(behavior_abl) + pp.Group(NAME).setResultsName("name") + \
                     O_PAR + pp.delimitedList(NAME + NAME) + C_PAR + O_BRACKET

    spawn_at_stmt = s(pp.Literal('at')) + NAME
    spawn_stmt        = pp.Or([spawn_abl, subgoal_abl, act_abl]) + NAME + O_PAR +\
        pp.delimitedList(NAME) + C_PAR + pp.Optional(spawn_at_stmt) + SEMICOLON

    step_stmt         = pp.Or([succeed_abl, fail_abl])

    spec_stmt         = s(specificity_abl) + NUM
    priority_stmt     = s(priority_abl) + NUM

    success_test_stmt = s(success_test_abl) + O_BRACKET \
        + pp.Optional(pp.SkipTo(C_BRACKET, include=True)).setResultsName("contents")

    with_head = s(with_abl) + O_PAR + pp.delimitedList(pp.Or([success_test_stmt,
                                                              priority_stmt,
                                                              ignore_failure_abl,
                                                              persistent_abl])) + C_PAR

    single_with_stmt = with_head.setResultsName('head') \
        + pp.Or([spawn_stmt, step_stmt, wait_abl]).setResultsName('target') + SEMICOLON

    single_mental_stmt = s(mental_abl) + O_BRACKET \
        + pp.Optional(pp.SkipTo(C_BRACKET, include=True)).setResultsName('contents')

    multi_line_open = pp.SkipTo(O_BRACKET)
    #----------------------------------------
    # Parse Actions
    beh_ent_stmt.setParseAction(      lambda x: ABS.AblEnt(x[0]))
    register_act_stmt.setParseAction( lambda x: ABS.AblRegistration(x[0], obj_e.ACT))
    register_wme_stmt.setParseAction( lambda x: ABS.AblRegistration(x[0], obj_e.WME))
    conflict_stmt.setParseAction(     lambda x: ABS.AblRegistration(x[:], obj_e.CONFLICT))
    import_stmt.setParseAction(       lambda x: ABS.AblMisc('import', args=[x[:]]))

    behavior_stmt.setParseAction(     lambda x: ABS.AblBehavior(x.name[0],
                                                           args=x.args[:] + [x.form]))

    spawn_at_stmt.setParseAction(lambda x: ABS.AblComponent(x[1], obj_e.SPAWNTARGET))
    spawn_stmt.setParseAction(        lambda x: ABS.AblComponent(x[1], obj_e.SPAWN,
                                                            args=[x[0]]))
    step_stmt.setParseAction(         lambda x: ABS.AblComponent(x[0], obj_e.STEP))
    spec_stmt.setParseAction(         lambda x: ABS.AblComponent(type=obj_e.SPEC,
                                                            args=[float(x[0])]))
    priority_stmt.setParseAction(     lambda x: ABS.AblComponent(type=obj_e.PRIORITY,
                                                            args=[float(x[0])]))

    success_test_stmt.setParseAction(lambda x: ABS.AblComponent(type=obj_e.SUCCTEST,
                                                           args=[x.contents]))
    single_with_stmt.setParseAction(build_with_stmt)
    single_mental_stmt.setParseAction(lambda x: ABS.AblComponent(type=obj_e.MENTAL,
                                                            args=[x.contents]))
    multi_line_open.setResultsName(lambda x: False)


    initial_abl.setParseAction(       lambda x: ABS.AblBehavior("initial_tree"))


    pass_stmt = pp.restOfLine
    pass_stmt.setParseAction(lambda x: ParseBase('Pass', args=x[:]))

    com_parser = pp.dblSlashComment
    com_parser.setParseAction(lambda x: obj_e.COMMENT)

    # Final Assembly
    single_line_parser = pp.MatchFirst([com_parser,
                                        import_stmt,
                                        initial_abl,
                                        beh_ent_stmt,
                                        register_act_stmt,
                                        register_wme_stmt,
                                        conflict_stmt,
                                        behavior_stmt,
                                        multi_line_open,
                                        pass_stmt])

    return single_line_parser


def build_multi_line_parser():
    # wme definition
    var_def = NAME + NAME + pp.SkipTo(SEMICOLON, include=True)
    wme_def = s(wme_abl) + NAME + O_BRACKET \
        + pp.OneOrMore(var_def).setResultsName('defs') \
        + C_BRACKET

    # mental/precons/success_tests consume till closed
    # TODO ensure brackets are balanced
    mental_stmt       = s(mental_abl) + O_BRACKET + pp.Optional(pp.SkipTo(C_BRACKET, include=True)).setResultsName('contents')
    precondition_stmt = s(precond_abl) + O_BRACKET + pp.Optional(pp.SkipTo(C_BRACKET, include=True)).setResultsName('contents')
    success_test_stmt = s(success_test_abl) + O_BRACKET + pp.Optional(pp.SkipTo(C_BRACKET, include=True)).setResultsName('contents')

    spawn_at_stmt = s(pp.Literal('at')) + NAME
    spawn_stmt        = pp.Or([spawn_abl, subgoal_abl, act_abl]) + NAME + O_PAR +\
        pp.delimitedList(NAME).setResultsName('args') + C_PAR \
        + pp.Optional(spawn_at_stmt).setResultsName('spawnAt')
    step_stmt = pp.Or([succeed_abl, fail_abl])
    priority_stmt     = s(priority_abl) + NUM
    # with statements
    with_head = with_abl + O_PAR + pp.delimitedList(pp.Or([success_test_stmt,
                                                           priority_stmt,
                                                           ignore_failure_abl,
                                                           persistent_abl])) + C_PAR

    with_stmt = with_head.setResultsName('head') \
        + pp.Or([spawn_stmt, wait_abl, step_stmt]).setResultsName('target') + SEMICOLON

    # Actions
    mental_stmt.setParseAction(lambda x: ABS.AblComponent(type=obj_e.MENTAL,
                                                     args=[x.contents]))

    precondition_stmt.setParseAction( lambda x: ABS.AblComponent(type=obj_e.PRECON,
                                                            args=[x.contents]))
    var_def.setParseAction(lambda x: x[:])
    wme_def.setParseAction(lambda x: ABS.AblComponent(x[0],
                                                 type=obj_e.WME,
                                                 args=x.defs))
    precondition_stmt.setParseAction(lambda x: ABS.AblComponent(type=obj_e.PRECON,
                                                           args=[x[:]]))
    success_test_stmt.setParseAction(lambda x: ABS.AblComponent(type=obj_e.SUCCTEST,
                                                           args=[x.contents]))
    spawn_at_stmt.setParseAction(lambda x: ABS.AblComponent(x[1], obj_e.SPAWNTARGET))
    spawn_stmt.setParseAction(        lambda x: ABS.AblComponent(x[1], obj_e.SPAWN,
                                                            args=[x[0]] + [x.spawnAt] + x.args[:]))
    step_stmt.setParseAction(         lambda x: ABS.AblComponent(x[0], obj_e.STEP))
    priority_stmt.setParseAction(     lambda x: ABS.AblComponent(type=obj_e.PRIORITY,
                                                            args=[float(x[0])]))


    with_stmt.setParseAction(build_with_stmt)

    com_parser = pp.dblSlashComment
    com_parser.setParseAction(lambda x: obj_e.COMMENT)

    pass_stmt = pp.restOfLine
    pass_stmt.setParseAction(lambda x: ParseBase('Pass', args=x[:]))


    multi_line_parser = pp.MatchFirst([wme_def,
                                       mental_stmt,
                                       precondition_stmt,
                                       with_stmt,
                                       pass_stmt])



    return multi_line_parser
