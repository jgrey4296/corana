"""
Get cif rules files from data dir,

output to similarly named files in analysis directory
"""
import csv
import logging as root_logger
import re
from enum import Enum
from os import listdir
from os.path import (abspath, dirname, exists, expanduser, isdir, isfile, join,
                     split, splitext)
from random import shuffle

import code_analysis.util.analysis_case as AC
import code_analysis.util.utils as utils
import code_analysis.util.xml_utils as XU
import lxml
import pyparsing as pp
import spacy
from bs4 import BeautifulSoup

from cif_library_handler import cif_library_handler
from cif_state_handler import cif_state_handler
from promweek_handler import promweek_handler


LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################
nlp = spacy.load("en_core_web_sm")

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(split(filename)[1]))
    data = None

    with open(filename, 'rb') as f:
        text = f.read().decode('utf-8','ignore')

    soup = BeautifulSoup(text, features='lxml')

    ctx._misc['schema'] = XU.infer_schema(soup, schema=ctx._misc['schema'])

    # Handle File Type
    if soup.find('cifstate') is not None:
        data = cif_state_handler(filename, soup)
    elif soup.find('promweek') is not None:
        data = promweek_handler(filename, soup)
    elif soup.find('ciflibraries') is not None:
        data = cif_library_handler(filename, soup)
    else:
        raise Exception("Unrecognised xml rules: {}".format(filename))

    return data

def finalise_schema(_, ctx):
    schema = ctx._misc['schema']
    schema = {x : list(y) for x,y in schema.items()}
    ctx._misc['schema'] = schema

if __name__ == "__main__":
    target = join(dirname(__file__), "data", "CiFStates")
    input_ext = ".xml"

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    targets=[target],
                    _misc={'schema': None},
                    finalise=finalise_schema)()
