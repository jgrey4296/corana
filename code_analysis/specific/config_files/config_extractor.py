"""
Get ini files from data dir,

output to similarly named files in analysis directory
"""
import configparser
from enum import Enum
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
from random import shuffle
import pyparsing as pp

# Setup root_logger:
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
D3_TYPE = Enum("D3 Type", "STRINGS ATTACKS DILEMMAS EVENTS NAMES OTHER")

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = { }
    config = configparser.ConfigParser(allow_no_value=True, interpolation=None)
    with open(filename, 'rb') as f:
        text = f.read().decode('utf-8','ignore')

    try:
        config.read_string(text)

        # Assign file category
        d3e = D3_TYPE.OTHER
        if 'strings' in filename:
            d3e = D3_TYPE.STRINGS
        elif 'attacks' in filename:
            d3e = D3_TYPE.ATTACKS
        elif 'dilemmas' in filename:
            d3e = D3_TYPE.DILEMMAS
        elif 'events' in filename:
            d3e = D3_TYPE.EVENTS
        elif 'names' in filename:
            d3e = D3_TYPE.NAMES
        data['file_category'] = d3e

        data['keys'] = config.sections()
        for section in config.sections():
            data["{}_names".format(section)] = [x[0] for x in config.items(section)]
            data["{}_values".format(section)] = [x[1] for x in config.items(section)]


    except configparser.ParsingError as e:
        logging.warning("Parse Error: {}".format(str(e)))
        data['parse_error'] = str(e)

    return data

def accumulator(new_data, accumulator_data, ctx):

    # strings

    # attacks

    # dilemmas

    # events

    # names



    return accumulator_data


if __name__ == "__main__":
    input_ext = [".ini", ".txt"]
    output_ext = ".config_analysis"
    accum_data = {
        'strings' : {},
        'attacks' : {},
        'dilemmas' : {},
        'events' : {},
        'names' : {}
        }

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file,
                    output_ext,
                    accumulator=accumulator
                    )()
