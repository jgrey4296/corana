"""
Get abl files from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
import logging as root_logger
from enum import Enum
from os import listdir
from os.path import (abspath, dirname, exists, expanduser, isdir, isfile, join,
                     split, splitext)
from random import shuffle

import matplotlib.pyplot as plt
import networkx as nx
import pygraphviz as pgv
import pyparsing as pp

import abl_struct as ABS
import code_analysis.util.analysis_case as AC
import code_analysis.util.utils as utils
from code_analysis.util.parse_base import ParseBase

LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
# Enums:
obj_e = ABS.ABL_E

main_parser = None


def build_parser():
    """ Build a rough parser for abl """

    # Parser Keywords
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
    with_abl        = pp.Keyword("with")
    wme_abl         = pp.Keyword("wme")
    initial_abl     = pp.Keyword("initial_tree")
    succeed_abl     = pp.Keyword("succeed_step")
    fail_abl        = pp.Keyword("fail_step")
    conflict_abl    = pp.Keyword('conflict')
    import_abl      = pp.Keyword('import')

    parallel_abl.setParseAction(lambda x: "Parallel")
    sequential_abl.setParseAction(lambda x: "Sequential")

    beh_ent_stmt      = s(be_abl) + NAME
    register_act_stmt = s(register_abl + act_abl) + NAME
    register_wme_stmt = s(register_abl + wme_abl) + NAME

    behavior_stmt = (op(atomic_abl) +
                     op(joint_abl)).setResultsName("args") + \
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

    initial_abl.setParseAction(       lambda x: ABS.AblBehavior("initial_tree", [], True))
    import_stmt.setParseAction(       lambda x: ABS.AblMisc('import', x[:]))

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


def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = {'behaving_entity': "",
            'registrations': [],
            'behaviors': [],
            'behavior_edges' : [],
            'comments': 0}
    graph = nx.DiGraph()
    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()

    state = {'bracket_count' : 0,
             'current' : None,
             'line' : 0}
    while bool(lines):
        state['line'] += 1
        # logging.info("line: {}".format(state['line']))
        current = lines.pop(0)

        result = main_parser.parseString(current)[0]
        if not result:
            continue

        if isinstance(result, ParseBase):
            result.line_no = state['line']

        try:
            if result is obj_e.COMMENT:
                data['comments'] += 1
            elif isinstance(result, ABS.AblEnt):
                data['behaving_entity'] = result
            elif isinstance(result, ABS.AblRegistration):
                data['registrations'].append(result)
            elif isinstance(result, ABS.AblBehavior):
                state['current'] = result
                data['behaviors'].append(state['current'])
                if result.name not in graph:
                    graph.add_node(result.name)
            elif isinstance(result, ABS.AblComponent):
                state['current'].add_component(result)
                if result.type in [obj_e.PRECON, obj_e.SPEC]:
                    continue
                name = result.name
                if name is None:
                    name = str(result.type)
                if name not in graph:
                    graph.add_node(name)
                graph.add_edge(state['current'].name, name)
            elif not isinstance(result, ParseBase):
                logging.warning("Unrecognised parse result: {}".format(result))

        except AttributeError as err:
            breakpoint()
            logging.info("Error")

    # Convert graph into edgelist for data
    data['behavior_edges'] += list(nx.generate_edgelist(graph, data=False))

    # Draw graph
    # prog=[‘neato’|’dot’|’twopi’|’circo’|’fdp’|’nop’]


    if bool(graph):
        pgv_graph = nx.nx_agraph.to_agraph(graph)
        pgv_graph.layout(prog='dot')
        pgv_graph.draw(join(ctx._out_dir,
                            "{}.png".format(split(splitext(filename)[0])[1])))

    return data


if __name__ == "__main__":
    main_parser = build_parser()
    input_ext = ".abl"
    output_lists = ["behaviors"]
    output_ext = ".abl_analysis"


    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
