"""
Get tsv files from data dir,

output to similarly named files in analysis directory
"""
from random import choice
import re
import csv
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

def extract_from_file(filename):
    logging.info("Extracting from: {}".format(filename))
    with open(filename, 'rb') as f:
        text = [x.decode('utf-8','ignore') for x in f.readlines()]

    if "dialogue" in filename:
        data = handle_dialogue(text)

    return data

def handle_dialogue(text):
    data = {}
    csv_obj = csv.reader(text, delimiter="\t", quotechar='"')

    rows = [x for x in csv_obj]

    variables = list(set([y[0] for x in rows for y in re.findall("%(\w+)(\([\w,]*\))?%", x[0])]))

    data['length'] = len(rows)
    data['speech_acts'] = list(set([y for x in rows for y in x[1].split(',') if bool(y)]))
    data['num_speech_acts'] = len(data['speech_acts'])
    data['variables'] = variables

    # TODO parse text?

    return data


if __name__ == "__main__":
    queue = [join("data","tsv")]
    input_ext = ".tsv"
    output_lists = []
    output_ext = ".tsv_analysis"

    AC.AnalysisCase(queue,
                    input_ext,
                    extract_from_file,
                    output_lists,
                    output_ext)()
