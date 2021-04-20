"""
Get abl files from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
#imports
from os.path import join, isfile, exists, abspath, dirname
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp
import networkx as nx
import matplotlib.pyplot as plt
import pygraphviz as pgv
from enum import Enum

import code_analysis.util.analysis_case as AC
import code_analysis.util.utils as utils
from code_analysis.util.parse_base import ParseBase

# Setup root_logger:
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
# Enums:
ABL_E = Enum('ABL_E', 'ENT ACT WME CONFLICT BEH COM SPAWN MENTAL PRECON SPEC INIT STEP COMMENT')

main_parser = None

obj_e = ABL_E

class AblEnt(ParseBase):

    def __init__(self, name):
        super().__init__()
        self._type = obj_e.ENT
        self._name = name


class AblRegistration(ParseBase):

    def __init__(self, _type, name):
        super().__init__()
        assert(_type in [obj_e.WME, obj_e.ACT, obj_e.CONFLICT])
        self._type = _type
        self._name = name


class AblBehavior(ParseBase):

    def __init__(self, name, args, init=False):
        super().__init__()
        self._type = obj_e.BEH
        self._init = init
        self._name = name
        self._args += args

    def add_component(self, comp):
        self._components.append(comp)


class AblComponent(ParseBase):

    def __init__(self, _type, name=None, args=None):
        super().__init__()
        assert(_type in [obj_e.SPAWN, obj_e.MENTAL, obj_e.PRECON, obj_e.SPEC, obj_e.STEP])
        self._type = _type
        self._name = name
        if args:
            self._args += args

    def to_dict(self):
        _type = ""
        if self._type == obj_e.MENTAL:
            _type = "MentalAct"
        elif self._type == obj_e.PRECON:
            _type = "Precondition"
        elif self._type == obj_e.STEP:
            _type = "Step"
        elif self._type == obj_e.SPEC:
            _type = "Specificity"
        elif self._type == obj_e.SPAWN and 'subgoal' in self._args:
            _type = "SubGoal"
        elif self._type == obj_e.SPAWN and 'act' in self._args:
            _type = "Act"
        else:
            _type = "SpawnGoal"

        name = ""
        if self._name is not None:
            name = "{}".format(self._name)

        args = [str(x) for x in self._args if x not in ["act", "spawngoal", "subgoal"]]

        return { 'type' : _type, 'name': name, 'args': args }


class AblMisc(ParseBase):

    def __init__(self, iden, text):
        super().__init__()
        self._iden = iden
        self._text = text


def build_parser():

    # Parser Keywords
    s = pp.Suppress
    op = pp.Optional
    lineEnd = pp.lineEnd
    NAME = pp.Word(pp.alphanums + "_")
    NUM = pp.Word(pp.nums + ".")
    SEMICOLON = pp.Literal(";")
    O_BRACKET = pp.Literal('{')
    C_BRACKET = pp.Literal('}')

    act_abl = pp.Keyword("act")
    atomic_abl = pp.Keyword("atomic")
    be_abl = pp.Keyword("behaving_entity")
    behavior_abl = pp.Keyword("behavior")
    fail_abl = pp.Keyword("fail_step")
    joint_abl = pp.Keyword("joint")
    mental_abl = pp.Keyword("mental_act")
    parallel_abl = pp.Keyword("parallel")
    precond_abl = pp.Keyword("precondition")
    register_abl = pp.Keyword("register")
    sequential_abl = pp.Keyword("sequential")
    spawn_abl = pp.Keyword("spawngoal")
    specificity_abl = pp.Keyword("specificity")
    subgoal_abl = pp.Keyword("subgoal")
    with_abl = pp.Keyword("with")
    wme_abl = pp.Keyword("wme")
    initial_abl = pp.Keyword("initial_tree")
    succeed_abl = pp.Keyword("succeed_step")
    fail_abl = pp.Keyword("fail_step")
    conflict_abl = pp.Keyword('conflict')
    import_abl = pp.Keyword('import')

    parallel_abl.setParseAction(lambda x: "Parallel")
    sequential_abl.setParseAction(lambda x: "Sequential")

    beh_ent_stmt = s(be_abl) + NAME
    register_act_stmt = s(register_abl + act_abl) + NAME
    register_wme_stmt = s(register_abl + wme_abl) + NAME

    behavior_stmt = (op(atomic_abl) +
                     op(joint_abl)).setResultsName("args") + \
                     pp.Or([sequential_abl, parallel_abl]).setResultsName('form') + \
                     s(behavior_abl) + pp.Group(NAME).setResultsName("name")

    spawn_stmt = pp.Or([spawn_abl, subgoal_abl, act_abl]) + NAME
    skip_to_spawn = s(pp.SkipTo(spawn_stmt)) + spawn_stmt
    step_stmt = pp.Or([succeed_abl, fail_abl])
    skip_to_step = s(pp.SkipTo(step_stmt)) + step_stmt
    mental_stmt = mental_abl
    precondition_stmt = precond_abl
    spec_stmt = s(specificity_abl) + NUM
    conflict_stmt = s(conflict_abl) + NAME + NAME
    import_stmt = s(import_abl) + pp.restOfLine

    # Parse Actions
    beh_ent_stmt.setParseAction(lambda x: AblEnt(x[0]))
    register_act_stmt.setParseAction(lambda x: AblRegistration(obj_e.ACT, x[0]))
    register_wme_stmt.setParseAction(lambda x: AblRegistration(obj_e.WME, x[0]))
    conflict_stmt.setParseAction(lambda x: AblRegistration(obj_e.CONFLICT, x[:]))
    behavior_stmt.setParseAction(lambda x: AblBehavior(x['name'][0], x['args'][:] + [x['form']]))
    spawn_stmt.setParseAction(lambda x: AblComponent(obj_e.SPAWN, name=x[1], args=[x[0]]))
    step_stmt.setParseAction(lambda x: AblComponent(obj_e.STEP, x[0]))
    mental_stmt.setParseAction(lambda x: AblComponent(obj_e.MENTAL))
    precondition_stmt.setParseAction(lambda x: AblComponent(obj_e.PRECON))
    spec_stmt.setParseAction(lambda x: AblComponent(obj_e.SPEC, args=[float(x[0])]))
    initial_abl.setParseAction(lambda x: AblBehavior("initial_tree", [], True))
    import_stmt.setParseAction(lambda x: AblMisc('import', x[:]))

    pass_stmt = pp.restOfLine
    pass_stmt.setParseAction(lambda x: ParseBase())

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
            result._line_no = state['line']

        try:
            if result is obj_e.COMMENT:
                data['comments'] += 1
            elif isinstance(result, AblEnt):
                data['behaving_entity'] = result
            elif isinstance(result, AblRegistration):
                data['registrations'].append(result)
            elif isinstance(result, AblBehavior):
                state['current'] = result
                data['behaviors'].append(state['current'])
                if result._name not in graph:
                    graph.add_node(result._name)
            elif isinstance(result, AblComponent):
                state['current'].add_component(result)
                if result._type in [obj_e.PRECON, obj_e.SPEC]:
                    continue
                name = result._name
                if name is None:
                    name = str(result._type)
                if name not in graph:
                    graph.add_node(name)
                graph.add_edge(state['current']._name, name)
            elif not isinstance(result, ParseBase):
                logging.warning("Unrecognised parse result: {}".format(result))

        except AttributeError as e:
            breakpoint()

    # Convert graph into edgelist for data
    data['behavior_edges'] += list(nx.generate_edgelist(graph, data=False))

    # Draw graph
    # prog=[‘neato’|’dot’|’twopi’|’circo’|’fdp’|’nop’]
    if bool(graph):
        pgv_graph = nx.nx_agraph.to_agraph(graph)
        pgv_graph.layout(prog='dot')
        pgv_graph.draw(join('analysis',
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
