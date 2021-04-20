"""
Get csv tables from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
import csv
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp

# Setup root_logger:
from os.path import splitext, split
import logging as root_logger

import analysis_case as AC
import utils

LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
# Enums:
DTYPE = Enum("Democracy3 File Type", "ACHIEVEMENT POLICY POLICYGROUP PRESSUREGROUP SIMULATION SITUATION SLIDER VOTER NONE")


def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = { }

    with open(filename, 'rb') as f:
        text = [x.decode('utf-8','ignore') for x in f.readlines()]

    csv_obj = csv.DictReader(text, restkey="remaining", quotechar='"')

    rows = [x for x in csv_obj]

    keys = [x for x in rows[0].keys()]
    data['__keys'] = keys
    data['__length'] = len(rows)

    # Handle Different sources
    if "BBC" in filename:
        data.update(handleBBC(rows))
    elif "swda" in filename:
        data.update(handleDAMSL(rows))
    elif "democracy" in filename:
        data.update(handleDemocracy(rows, filename))
    elif "SQF" in filename:
        data.update(handleStopAndFrisk(rows))
    elif "Badge" in filename:
        data.update(handleBadge(rows))
    else:
        logging.info("Handling Generic")
        # TODO


    return data


def handleBBC(rows):
    data = { 'base_url' : 'http://bbcsfx.acropolis.org.uk/assets/{}',
             'sounds' : [],
             'categories' : set(),
    }
    for row in rows:
        data['categories'].add(row['category'])
        data['sounds'].append({
            'url' : row['location'],
            'desc' : row['description'],
            'len' : row['secs'],
            'tag' : row['category']
            })

    return data

def handleDAMSL(rows):
    data = {
        'meta' : [],
        'statements': []
    }
    keys = [x for x in rows[0].keys()]
    in_meta = False
    if 'swda_filename' not in keys:
        in_meta = True

    # TODO stats on utterances
    # TODO stats on call,response and balance of conv
    for row in rows:
        if in_meta:
            data['meta'].append({
                'topic' : row['topic_description'],
                'conv_id' : row['conversation_no'],
                'genders' : [row['from_caller_sex'],row['to_caller_sex']]
            })
        else:
            data['statements'].append({
                'conv_id' : row['conversation_no'],
                'transcript_index' : "{}.{}.{}".format(row['transcript_index'],
                                                       row['utterance_index'],
                                                       row['subutterance_index']),
                'speech_act_tag' : row['act_tag'],
                'caller' : row['caller'],
                'text' : row['text']
                })

    return data

def handleDemocracy(rows, filename):
    data = {}

    # Assign file type
    d3t = DTYPE.NONE
    if "achievement" in filename:
        d3t = DTYPE.ACHIEVEMENT
    elif "policies" in filename:
        d3t = DTYPE.POLICY
    elif "policygroups" in filename:
        d3t = DTYPE.POLICYGROUP
    elif "pressuregroups" in filename:
        d3t = DTYPE.PRESSUREGROUP
    elif "simulation" in filename:
        d3t = DTYPE.SIMULATION
    elif "situations" in filename:
        d3t = DTYPE.SITUATION
    elif "sliders" in filename:
        d3t = DTYPE.SLIDER
    elif "votertypes" in filename:
        d3t = DTYPE.VOTER

    if d3t is DTYPE.ACHIEVEMENT:
        continue
    elif d3t is DTYPE.POLICY:
        # collect guinames, description
        # collect introduce, cancel, raise, lower, mincost, maxcost
        continue
    elif d3t is DTYPE.POLICYGROUP:
        # collect names
        continue
    elif d3t is DTYPE.PRESSUREGROUP:
        # group by type, get names and their group (includes remaining)
        # collect threat level texts
        # collect radicalisation and de-radical rates
        continue
    elif d3t is DTYPE.SIMULATION:
        # collect names, description, zone
        # min, default, max triples
        # count emotions
        # formulas : [y for x in rows for y in x['remaining'] if y not in ['#','']]]
        continue
    elif d3t is DTYPE.SITUATION:
        # needs resetting to original from game
        # collect names
        continue
    elif d3t is DTYPE.SLIDER:
        # collect names, group by discrete type
        # collect values
        continue
    elif d3t is DTYPE.VOTER:
        # collect guinames, plural pairs
        # collect descriptions
        # collect influences / remaining
        continue


    return data

def handleStopAndFrisk(rows):
    data = {}
    # TODO handle stop and frisk data
    return data

def handleBadge(rows):
    data = {}
    # TODO handle badge data
    return data


if __name__ == "__main__":
    input_ext = ".csv"
    output_lists = []
    output_ext = ".csv_analysis"

    AC.AnalysisClass(__file__,
                     input_ext,
                     extract_from_file,
                     output_lists,
                     output_ext)()
