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

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

import handlers


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

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData(filename)

    with open(filename, 'rb') as f:
        text = [x.decode('utf-8','ignore') for x in f.readlines()]

    if "dialogue" in filename:
        data = handlers.handle_dialogue(text)

    return data


if __name__ == "__main__":
    input_ext = ".tsv"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
