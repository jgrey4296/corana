"""
Get DwarfFortress files from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
import datetime
import logging as root_logger
import re
from enum import Enum
from os import listdir
from os.path import (abspath, exists, expanduser, isdir, isfile, join, split,
                     splitext)
from random import shuffle

import code_analysis.util.analysis_case as AC
import pyparsing as pp
from bs4 import BeautifulSoup
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

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData(filename)
    soup = None
    with open(filename,'rb') as f:
        text = f.read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(text, features='lxml')

    assert(soup is not None)
    state = { 'bracket_count' : 0,
              'current' : None,
              'line' : 0}

    if "dota" in filename:
        handlers.handle_dota_patch_notes(data, soup)
    else:
        handlers.handle_df_patch_notes(data, soup)

    return data


if __name__ == "__main__":
    input_ext = ".html"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
