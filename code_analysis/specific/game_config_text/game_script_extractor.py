"""
Get setup scripts from 4x games from data dir,

output to similarly named files in analysis directory
"""
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp

import analysis_case as AC
import utils


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
# Enums:


def build_parser():

    return None

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = { }
    lines = []
    with open(filename,'r') as f:
        lines = f.readlines()

    # Send to handler
    if "CK2" in filename:
        data.update(handleCK2(lines))
    elif "EUIV" in filename:
        data.update(handleEUIV(lines))
    elif "democracy_3" in filename:
        data.update(handleDemocracy(lines))
    elif "distant_worlds" in filename:
        data.update(handleDistantWorlds(lines))
    elif "geck" in filename:
        data.update(handleGECK(lines))
    elif "prison_architect" in filename:
        data.update(handlePrisonArchitect(lines))
    elif "red_shirt" in filename:
        data.update(handleRedShirt(lines))
    elif "skyrim" in filename:
        data.update(handleSkyrim(lines))
    elif "stellaris" in filename:
        data.update(handleStellaris(lines))
    elif "witcher" in filename:
        data.update(handle_witcher(lines))
    else:
        logging.info("Handling generic")

    return data

#Stack based, uses:
## X = { : key + context open
## } : context close
## X = Y : assignment


# TODO extract predicates



def handleCK2(lines):
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
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleEUIV(lines):
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
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleDemocracy(lines):
    # TODO figure out what this needs
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleDistantWorlds(lines):
    # TODO distant worlds
    # TODO  policies
    # TODO get verbs
    # TODO get dialogue acts
    # TODO construct hostility matrix
    # TODO Government stats
    # TODO disease
    # TODO research tree
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleGECK(lines):
    # TODO load dialogue
    # TODO load ranks
    # TODO load quest objective text and stages
    # TODO load player topics
    # TODO get radio messages
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handlePrisonArchitect(lines):
    # TODO see if theres anything useful
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleRedShirt(lines):
    # TODO unknown
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleSkyrim(lines):
    # TODO look at civil war script
    # TODO find categorisations, like in actor.psc
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handleStellaris(lines):
    # TODO Stellaris
    # TODO message types
    # TODO policies
    # TODO governments
    # TODO event chains
    # TODO ethics
    # TODO edicts
    # TODO diplomatic actions
    # TODO Agendas
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data

def handle_witcher(lines):
    #see https://witcher.gamepedia.com/Witcher_Script
    # TODO get enums of attacks and actions
    # TODO get predicates
    # TODO get job tree
    # TODO get living world
    # TODO get NPC
    data = {}
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}
    while bool(lines):
        state['line'] += 1
        current = lines.pop(0)


    return data



if __name__ == "__main__":
    input_ext = ".txt"
    output_lists = []
    output_ext = ".game_analysis"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
