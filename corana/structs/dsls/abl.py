#!/usr/bin/env python
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import pyparsing as pp

from corana.util.parse_base import ParseBase
import abl_struct as ABS

obj_e = ABS.ABL_E

N               = lambda x,y : y.setResultsName(x)
s               = pp.Suppress
op              = pp.Optional
lineEnd         = pp.lineEnd
NAME            = pp.Word(pp.alphanums + "_-")
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
team_eff_abl    = pp.Keyword("team_effect_only")


with_abl           = pp.Keyword("with")
priority_abl       = pp.Keyword('priority')
priority_mod_abl   = pp.Keyword("priority_modifier")
persistent_abl     = pp.Keyword('persistent')
success_test_abl   = pp.Keyword('success_test')
ignore_failure_abl = pp.Keyword('ignore_failure')
teammembers_abl    = pp.Keyword('teammembers')

parallel_abl.setParseAction(   lambda x: "Parallel")
sequential_abl.setParseAction( lambda x: "Sequential")
wait_abl.setParseAction(           lambda x: ABS.AblComponent("wait", obj_e.STEP))
initial_abl.setParseAction(        lambda x: ABS.AblBehavior("initial_tree"))

def build_behavior(results):
    obj_args = []
    obj_args += results.args[:]
    obj_args.append(results.form)
    if 'params' in results:
        obj_args += [x[:] for x in results.params]

    obj = ABS.AblBehavior(results.name,
                          args=obj_args)
    return obj

def build_spawn_stmt(results):
    obj_args = [results[0]]
    if 'spawnAt' in results:
        obj_args += [results.spawnAt]
    if 'args' in results:
        obj_args += results.args[:]

    return ABS.AblComponent(results[1], obj_e.SPAWN,
                            args=obj_args)

def build_with_stmt(results):
    target   = results.target[0]
    obj_args = []

    if 'head' not in results:
        return target

    for obj in results.head[:]:
        # convert the head components to simple strings
        if isinstance(obj, str):
            obj_args.append(obj)
        elif isinstance(obj, ABS.AblComponent):
            as_dict = obj.to_dict()
            simplified = [as_dict['type']] + as_dict['args']
            obj_args.append(simplified)
        else:
            logging.warning(f"Unrecognised with_head element: {obj}")

    target.args += obj_args
    return target

beh_ent_stmt       = s(be_abl) + NAME
beh_ent_stmt.setParseAction(       lambda x: ABS.AblEnt(x[0]))

behavior_stmt      = N("args", op(atomic_abl) + op(joint_abl)) + N("form", pp.Or([sequential_abl, parallel_abl])) + s(behavior_abl) + N("name", NAME) + O_PAR + N("params", op(pp.delimitedList(pp.Group(NAME + NAME)))) + C_PAR + O_BRACKET
behavior_stmt.setParseAction(build_behavior)

conflict_stmt      = s(conflict_abl) + NAME + pp.OneOrMore(NAME)
conflict_stmt.setParseAction(      lambda x: ABS.AblRegistration(x[:], obj_e.CONFLICT))

import_stmt        = s(import_abl) + pp.restOfLine
import_stmt.setParseAction(        lambda x: ABS.AblMisc('import', args=[y.strip() for y in x[:]]))

mental_stmt        = s(mental_abl) + O_BRACKET + N("contents", pp.Optional(pp.SkipTo(C_BRACKET, include=True)))
mental_stmt.setParseAction(        lambda x: ABS.AblComponent(type=obj_e.MENTAL, args=[x.contents]))

precondition_stmt  = s(precond_abl) + O_BRACKET + N("contents", pp.Optional(pp.SkipTo(C_BRACKET, include=True)))
precondition_stmt.setParseAction(  lambda x: ABS.AblComponent(type=obj_e.PRECON, args=[x.contents]))

priority_stmt      = s(pp.Or([priority_abl, priority_mod_abl])) + NUM
priority_stmt.setParseAction(      lambda x: ABS.AblComponent(type=obj_e.PRIORITY, args=[float(x[0])]))

register_act_stmt  = s(register_abl + act_abl) + NAME + with_abl + NAME
register_act_stmt.setParseAction(  lambda x: ABS.AblRegistration(x[0], obj_e.ACT))

register_wme_stmt  = s(register_abl + wme_abl) + NAME + with_abl + NAME
register_wme_stmt.setParseAction(  lambda x: ABS.AblRegistration(x[0], obj_e.WME))

spawn_at_stmt      = s(pp.Literal('at')) + NAME
spawn_at_stmt.setParseAction(      lambda x: ["spawntarget", x[1]])

spawn_stmt         = pp.Or([spawn_abl, subgoal_abl, act_abl]) + NAME + O_PAR + N("args", op(pp.delimitedList(NAME))) + C_PAR + N("spawnAt", pp.Optional(spawn_at_stmt))
spawn_stmt.setParseAction(build_spawn_stmt)

spec_stmt          = s(specificity_abl) + NUM
spec_stmt.setParseAction(          lambda x: ABS.AblComponent(type=obj_e.SPEC, args=[float(x[0])]))

step_stmt          = pp.Or([succeed_abl, fail_abl])
step_stmt.setParseAction(          lambda x: ABS.AblComponent(x[0], obj_e.STEP))

success_test_stmt  = s(success_test_abl) + O_BRACKET + N("contents", pp.Optional(pp.SkipTo(C_BRACKET, include=True)))
success_test_stmt.setParseAction(  lambda x: ABS.AblComponent(type=obj_e.SUCCTEST, args=[x.contents]))

var_def            = NAME + NAME + pp.SkipTo(SEMICOLON, include=True)
var_def.setParseAction(            lambda x: x[:])

with_head          = s(with_abl) + O_PAR + pp.delimitedList(pp.Or([success_test_stmt, priority_stmt, ignore_failure_abl, persistent_abl, team_eff_abl])) + C_PAR

with_stmt          = op(N("head", with_head)) + N("target", pp.Or([spawn_stmt, wait_abl, step_stmt])) + SEMICOLON
with_stmt.setParseAction(build_with_stmt)

wme_def            = s(wme_abl) + NAME + O_BRACKET + N("defs", pp.OneOrMore(var_def)) + C_BRACKET
wme_def.setParseAction(            lambda x: ABS.AblComponent(x[0], type=obj_e.WME, args=x.defs))

pass_stmt = pp.restOfLine.copy()
pass_stmt.setParseAction(lambda x: ParseBase('Pass', args=x[:]))

com_parser = pp.javaStyleComment

multi_line_open    = pp.Or([pp.Literal("/**"),
                            pp.Regex(".+{$")])
multi_line_open.setParseAction(    lambda x: False)

continue_ml = pp.restOfLine.copy()
continue_ml.setParseAction(lambda x: False)

end_ml = pp.Regex(".*}$")
end_ml.setParseAction(lambda x: ParseBase("Pass", args=x[:]))

def build_parser():
    """ Build a rough parser for abl """
    return build_single_line_parser(), build_multi_line_parser()

def build_single_line_parser():

    # Final Assembly
    single_line_parser = pp.MatchFirst([import_stmt,
                                        initial_abl,
                                        beh_ent_stmt,
                                        register_act_stmt,
                                        register_wme_stmt,
                                        conflict_stmt,
                                        behavior_stmt,
                                        precondition_stmt,
                                        multi_line_open,
                                        with_stmt,
                                        mental_stmt,
                                        pass_stmt])
    single_line_parser.ignore(com_parser)

    return single_line_parser


def build_multi_line_parser():

    multi_line_parser = pp.MatchFirst([wme_def,
                                       mental_stmt,
                                       precondition_stmt,
                                       with_stmt,
                                       end_ml,
                                       continue_ml])
    multi_line_parser.ignore(com_parser)

    return multi_line_parser
