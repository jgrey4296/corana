"""
Get xml files of text (usc, the bible etc) from data dir,

output to similarly named files in analysis directory
"""
import csv
import logging as root_logger
import re
from enum import Enum
from os import listdir
from os.path import (abspath, exists, expanduser, isdir, isfile, join, split,
                     splitext)
from random import shuffle

import code_analysis.util.analysis_case as AC
import lxml
import pyparsing as pp
import spacy
from bs4 import BeautifulSoup
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
nlp = spacy.load("en_core_web_sm")

KJV_RE = re.compile('kjv([0-9]+)(O|A)z([0-9]+)z([0-9]+)')


def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData(filename)

    with open(filename, 'rb') as f:
        text = f.read().decode('utf-8','ignore')

    soup = BeautifulSoup(text, features='lxml')

    # Handle File Type
    if 'wow_quests' in filename:
        data = parse_wow_quest(data, soup)
    elif "trump" in filename:
        data = parse_trump(data, soup)
    elif "kjv" in filename:
        data = parse_bible(data, soup)
    elif "usc" in filename:
        data = parse_usc(data, soup)
    elif "dragon" in filename:
        data = parse_king_dragon_pass(data, soup)
    elif "roberts" in filename:
        data = parse_roberts_rules(data, soup)
    elif "twine" in filename:
        data = parse_twine(data, soup)
    elif "unrest" in filename:
        data = parse_unrest(data, soup)
    else:
        logging.warning(f"Unrecognized: {filename}")
        data.flag("discard")

    return data



if __name__ == "__main__":
    base = join(dirname(__file__), "data")
    targets = [join(base, x) for x in ["uscode",
                                       "king_james_bible",
                                       "red_shirt",
                                       "king_dragon_pass",
                                       "dwarf_fortress",
                                       "unrest",
                                       "twine"]]
    input_ext = [".xml", ".html"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    targets=targets)()
