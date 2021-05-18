"""
Get DwarfFortress files from data dir,
extract names of behaviours mentioned
output to similarly named files in analysis directory
"""
import datetime
import re
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp
from bs4 import BeautifulSoup
import spacy

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

# Setup root_logger:
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

nlp = spacy.load("en_core_web_sm")

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData(filename)
    soup = None
    with open(filename,'rb') as f:
        text = f.read().decode('utf-8', 'ignore')
        soup = BeautifulSoup(text, features='lxml')

    assert(soup is not None)
    extract_from_dev_log(soup, data)

    return data

def extract_from_dev_log(soup, data):
    dev_list = soup.find('ul')

    try:
        #Add (date : text)
        for li in dev_list.children:
            span = li.find('span')
            if span is None or span == -1:
                continue
            date = span.string
            text = li.get_text()
            text = text.replace(date,"")
            text = text.replace('\n',' ')
            data[date] = text
    except AttributeError:
        breakpoint()



if __name__ == "__main__":
    input_ext = ".html"

    init_accum = {
        '__total_count' : 0,
        '__sen_counts'  : {},
        '__unique_words' : set()
        }


    AC.AnalysisClass(__file__,
                     input_ext,
                     extract_from_file)()
