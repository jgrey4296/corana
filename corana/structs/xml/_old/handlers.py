#!/usr/bin/env python3
import logging as root_logger
logging = root_logger.getLogger(__name__)

from corana.util.parse_state import ParseState

def handle_CK2(data, lines):
    # TODO CK2/EUIV scripts
    # TODO  decision files?
    # TODO  traits, religions!
    # TODO factions, titles,
    # TODO law, jobs, actions
    # TODO government
    # TODO execution methods
    # TODO disease, death,
    # TODO cultures
    # TODO council voting/positions
    # TODO buildings
    # TODO policies

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_EUIV(data, lines):
    # TODO CK2/EUIV scripts
    # TODO  decision files?
    # TODO  traits, religions!
    # TODO factions, titles,
    # TODO law, jobs, actions
    # TODO government
    # TODO execution methods
    # TODO disease, death,
    # TODO cultures
    # TODO council voting/positions
    # TODO buildings
    # TODO policies

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_Democracy(data, lines):
    # TODO figure out what this needs


    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_DistantWorlds(data, lines):
    # TODO distant worlds
    # TODO  policies
    # TODO get verbs
    # TODO get dialogue acts
    # TODO construct hostility matrix
    # TODO Government stats
    # TODO disease
    # TODO research tree

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_GECK(data, lines):
    # TODO load dialogue
    # TODO load ranks
    # TODO load quest objective text and stages
    # TODO load player topics
    # TODO get radio messages

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_PrisonArchitect(data, lines):
    # TODO see if theres anything useful

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_RedShirt(data, lines):
    # TODO unknown

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_Skyrim(data, lines):
    # TODO look at civil war script
    # TODO find categorisations, like in actor.psc

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_Stellaris(data, lines):
    # TODO Stellaris
    # TODO message types
    # TODO policies
    # TODO governments
    # TODO event chains
    # TODO ethics
    # TODO edicts
    # TODO diplomatic actions
    # TODO Agendas

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_witcher(data, lines):
    #see https://witcher.gamepedia.com/Witcher_Script
    # TODO get enums of attacks and actions
    # TODO get predicates
    # TODO get job tree
    # TODO get living world
    # TODO get NPC

    state = ParseState()
    # state = { 'bracket_count' : 0,
    #           'current' : None,
    #           'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data
