#!/usr/bin/env python
import pyparsing as pp
import versu_struct as VS

import logging as root_logger
logging = root_logger.getLogger(__name__)

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

ALL_WRAP  = op(O_PAR) + ALL
SOME_WRAP = op(O_PAR) + SOME

# TODO Versu Keywords:
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


def build_parser():
    """
    Build a rough parser for versu text
    """

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
    block_p.setParseAction(lambda x: VS.VersuBlock(x.rest.strip(), x.head[0]))
    exp_p.setParseAction(lambda x: VS.VersuExpression(x.rest.strip(), x.head[0], hand=x.hand))
    misc_p.setParseAction(lambda x: VS.VersuExpression(x.rest.strip(), "statement"))
    end_p.setParseAction(lambda x: VS.versu_e.END)

    #double slash comment
    comment_line  = pp.dblSlashComment
    comment_open  = pp.Literal('/*') + pp.restOfLine
    comment_close = pp.SkipTo(pp.Literal('*/'))

    comment_line.setParseAction(lambda x: VS.versu_e.COMMENT)
    comment_open.setParseAction(lambda x: VS.versu_e.COPEN)
    comment_close.setParseAction(lambda x: VS.versu_e.CCLOSE)
    comment_parser = pp.Or([pp.dblSlashComment,
                            comment_open,
                            comment_close
                            ])

    O_BRACKET.setParseAction(lambda x: VS.versu_e.ODEF)
    C_BRACKET.setParseAction(lambda x: VS.versu_e.CDEF)
    closure_parser = pp.Or([O_BRACKET, C_BRACKET])

    main_parser = pp.MatchFirst([comment_parser,
                                 closure_parser,
                                 end_p,
                                 block_p,
                                 exp_p,
                                 misc_p,
                                 pp.restOfLine])

    return main_parser
