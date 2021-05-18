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

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

import handlers

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
    data = ParseData(filename)

    with open(filename, 'rb') as f:
        text = [x.decode('utf-8','ignore') for x in f.readlines()]

    csv_obj = csv.DictReader(text, restkey="remaining", quotechar='"')

    rows = [x for x in csv_obj]

    keys = [x for x in rows[0].keys()]
    data['__keys'] = keys
    data['__length'] = len(rows)

    # Handle Different sources
    if "BBC" in filename:
        data.update(handlers.handleBBC(rows))
    elif "swda" in filename:
        data.update(handlers.handleDAMSL(rows))
    elif "democracy" in filename:
        data.update(handlers.handleDemocracy(rows, filename))
    elif "SQF" in filename:
        data.update(handlers.handleStopAndFrisk(rows))
    elif "Badge" in filename:
        data.update(handlers.handleBadge(rows))
    else:
        logging.info("Handling Generic")
        # TODO


    return data


if __name__ == "__main__":
    input_ext = ".csv"

    AC.AnalysisClass(__file__,
                     input_ext,
                     extract_from_file)()
