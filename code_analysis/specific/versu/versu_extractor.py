"""
Get versu files from data dir,

output to similarly named files in analysis directory
"""
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase

# Setup root_logger:
from os.path import splitext, split
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################

versu_e = Enum('Versu Enums', 'COMMENT COPEN CCLOSE ODEF CDEF TOPEN END PATCH RANDOM')

Enum_to_String = {
    versu_e.TOPEN  : "type",
    versu_e.PATCH  : "patch",
    versu_e.RANDOM : "random"
    }

Quote_Extractor = pp.ZeroOrMore(pp.Suppress(pp.SkipTo(pp.quotedString)) + pp.quotedString)

class VersuBlock(ParseBase):

    def __init__(self, blockType, text):
        super().__init__()
        self._type = blockType
        self._name = text
        if blockType in Enum_to_String:
            self._type = Enum_to_String[blockType]
        else:
            logging.warning("Non-Enum Block Type: {}".format(str(blockType)))


class VersuExpression(ParseBase):

    def __init__(self, expressionType, text, hand=None):
        super().__init__()
        self._type = expressionType
        self._name = text
        self._block = None
        if bool(hand):
            self._args.append('hand_ordered')

#----------------------------------------
def build_parser():
    """
    Build a rough parser for versu text
    """

    # Versu Keywords:
    # to in test pick
    # assert_count_nodes assert_count_terms assert_count_removals assert_count_processes
    # increment decrement change_by create destroy load can_stit stit score_action
    # test_clear_undo test_undo test_find_subs test_process_autonomy test_all test_autonomy test_evaluate
    # assert_count_actions_available test_tick_processes perform_action assert_text_sub assert_count_free_object_pool
    # process_name process_menu test_clear_definitions definition debug_break count abs sign log
    # align_center align_left align_right ignore restriction
    # dot colon bang game_over append_text compute_reasons_for_action untyped_function append_text_capitalize
    # clear_clicks add_logical_breakpoint can_perform data do_patches cached_condition
    # update_achievement_stats praxis placement

    s         = pp.Suppress
    op        = pp.Optional
    lineEnd   = pp.lineEnd
    NAME      = pp.Word(pp.alphanums + "_")
    NUM       = pp.Word(pp.nums + ".")
    SEMICOLON = pp.Literal(";")
    O_BRACKET = pp.Literal('{')
    C_BRACKET = pp.Literal('}')
    O_PAR     = pp.Literal('(')
    C_PAR     = pp.Literal(')')

    FUN     = pp.Keyword('function')
    PROCESS = pp.Keyword('process')
    TYPES   = pp.Keyword('types')
    END     = pp.Keyword('end')
    START   = pp.Keyword('start')
    ACTION  = pp.Keyword('action')
    PRECON  = pp.Keyword('preconditions')
    POSTCON = pp.Keyword('postconditions')
    IF_p    = pp.Keyword('if')
    THEN    = pp.Keyword('then')
    ELSE    = pp.Keyword('else')
    CALL    = pp.Keyword('call')
    TEXT    = pp.Keyword('text')
    INSERT  = pp.Keyword('insert')
    HAND    = pp.Keyword('hand_ordered')
    DOM     = pp.Keyword('dominating')
    DEL     = pp.Keyword('delete')
    STATE   = pp.Keyword('state')
    PATCH   = pp.Keyword('patch')
    RANDOM  = pp.Keyword('random')
    IMPORT  = pp.Keyword('import')
    LOOP    = pp.Keyword('loop')
    MENU    = pp.Keyword('menu')
    ASSERT  = pp.Keyword('assert')
    ALL     = pp.Keyword('all')
    SOME    = pp.Keyword('some')

    ALL_WRAP = op(O_PAR) + ALL
    SOME_WRAP = op(O_PAR) + SOME

    add_p = pp.Literal('add_') + pp.Word(pp.alphas)
    add_p.setParseAction(lambda x: "".join(x[:]))

    on_p = pp.Literal('on_') + pp.Word(pp.alphas)
    on_p.setParseAction(lambda x: "".join(x[:]))

    block_p = pp.Or([TYPES, FUN, RANDOM,
                     PATCH, PROCESS, on_p,
                     ALL, SOME]).setResultsName('head') + pp.restOfLine.setResultsName('rest')

    exp_p = op(HAND).setResultsName('hand') \
        + pp.Or([ACTION, INSERT, CALL,
                 DEL, TEXT, IMPORT, IF_p,
                 THEN, PRECON, POSTCON,
                 LOOP, MENU, ASSERT, ELSE,
                 DOM, add_p]).setResultsName('head') + pp.restOfLine.setResultsName('rest')

    misc_p = pp.restOfLine.setResultsName('rest')
    end_p      = s(END)

    #result construction:
    block_p.setParseAction(lambda x: VersuBlock(x.head[0], x.rest.strip()))
    exp_p.setParseAction(lambda x: VersuExpression(x.head[0], x.rest.strip(), hand=x.hand))
    misc_p.setParseAction(lambda x: VersuExpression("statement", x.rest.strip()))
    end_p.setParseAction(lambda x: versu_e.END)

    #double slash comment
    comment_line  = pp.dblSlashComment
    comment_open  = pp.Literal('/*') + pp.restOfLine
    comment_close = pp.SkipTo(pp.Literal('*/'))

    comment_line.setParseAction(lambda x: versu_e.COMMENT)
    comment_open.setParseAction(lambda x: versu_e.COPEN)
    comment_close.setParseAction(lambda x: versu_e.CCLOSE)
    comment_parser = pp.Or([pp.dblSlashComment,
                            comment_open,
                            comment_close
                            ])

    O_BRACKET.setParseAction(lambda x: versu_e.ODEF)
    C_BRACKET.setParseAction(lambda x: versu_e.CDEF)
    closure_parser = pp.Or([O_BRACKET, C_BRACKET])

    main_parser = pp.MatchFirst([comment_parser,
                                 closure_parser,
                                 end_p,
                                 block_p,
                                 exp_p,
                                 misc_p,
                                 pp.restOfLine])

    return main_parser

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    main_parser = build_parser()
    #Data to return:
    data = { 'comments' : 0,
             'strings' : [],
             'non_exclusions' : 0,
             'exclusions' : 0,
             'in_order' : [],

             'blocks' : [],
             'functions' : [],
             'inserts' : [],
             'types' : [],
             'actions' : [],
            }

    #Read the file:
    lines = []
    with open(filename,'rb') as f:
        lines = [x.decode('utf-8','ignore') for x in f.readlines()]

    #Intermediate parsing state:
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0,
              'in_block' : [],
              'block_text' : None,
              'in_def' : None,
              'def_prefix' : None,
              'last_line' : None,
              'fold_into_last' : False}
    #Parse:
    while bool(lines):
        state['line'] += 1
        # TODO strip comments
        # TODO construct trie
        # logging.info("Line: {}".format(state['line']))
        current = lines.pop(0).strip()

        #Handle simple syntax cues
        if current == "":
            continue
        if state['fold_into_last']:
            current = state['last_line'] + current
            state['fold_into_last'] = False
        if current == "{":
            state['in_def'] = True
            state['def_prefix'] = state['last_line']
            continue
        elif current == "}":
            state['in_def'] = None
            continue

        if state['in_def'] and state['def_prefix']:
            current = "{}.{}".format(state['def_prefix'],current)

        #PARSE
        result = main_parser.parseString(current)[0]

        if isinstance(result, ParseBase):
            result._line_no = state['line']

        #Handle Blocks:
        if result is versu_e.COPEN: #comment
            data['comments'] += 1
            state['in_block'].append(versu_e.COMMENT)
            continue
        elif result is versu_e.CCLOSE: #comment close
            data['comments'] += 1
            state['in_block'].pop()
            continue
        elif bool(state['in_block']) and state['in_block'][-1] is versu_e.COMMENT or result is versu_e.COMMENT:
            data['comments'] += 1
            continue
        elif current[-1] == "." or current[-1] == "!":
            state['last_line'] = current
            state['fold_into_last'] = True
            continue

        elif isinstance(result, VersuBlock):
            state['in_block'].append(result)
            data['in_order'].append(result)
            data['blocks'].append(result)
            if result._type == "function":
                data['functions'].append(result)

        elif result is versu_e.END: #block end
            ending = state['in_block']
            if bool(state['in_block']):
                state['in_block'].pop()
            #TODO COPY and END
            end_exp = VersuExpression('end','')
            end_exp._line_no = state['line']
            data['in_order'].append(end_exp)

        #Handle Expressions:
        elif isinstance(result, VersuExpression):
            #TODO: Add block height
            data['in_order'].append(result)
            if result._type == 'insert':
                data['inserts'].append(result)
            elif result._type == "action":
                data['actions'].append(result)
            elif bool(state['in_block']) and isinstance(state['in_block'][-1], VersuBlock) and state['in_block'][-1]._type == "types":
                data['types'].append(result)


        #Handle other simple syntax based counts:
        data['non_exclusions'] += current.count('.')
        data['exclusions'] += current.count('!')

        potential_strings = Quote_Extractor.parseString(current)
        data['strings'] += potential_strings[:]


        state['last_line'] = current

    # TODO Export into trie-explorer usable format


    data['in_order'].sort()
    return data


if __name__ == "__main__":
    input_ext    = [".type", ".data", ".praxis"]
    output_lists = ['in_order']
    output_ext   = ".versu_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
