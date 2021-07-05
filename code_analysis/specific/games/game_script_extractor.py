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

def extract_from_file(filename, ctx):
    logging.info("Extracting from: {}".format(filename))
    data = ParseData(filename)
    lines = []
    with open(filename,'r') as f:
        lines = f.readlines()

    # Send to handler
    if "CK2" in filename:
        data.update(handlers.handle_CK2(data, lines))
    elif "EUIV" in filename:
        data.update(handlers.handle_EUIV(data, lines))
    elif "democracy_3" in filename:
        data.update(handlers.handle_Democracy(data, lines))
    elif "distant_worlds" in filename:
        data.update(handlers.handle_DistantWorlds(data, lines))
    elif "geck" in filename:
        data.update(handlers.handle_GECK(data, lines))
    elif "prison_architect" in filename:
        data.update(handlers.handle_PrisonArchitect(data, lines))
    elif "red_shirt" in filename:
        data.update(handlers.handle_RedShirt(data, lines))
    elif "skyrim" in filename:
        data.update(handlers.handle_Skyrim(data, lines))
    elif "stellaris" in filename:
        data.update(handlers.handle_Stellaris(data, lines))
    elif "witcher" in filename:
        data.update(handlers.handle_witcher(data, lines))
    else:
        logging.warning(f"Unrecognized: {filename}")
        data.flag("discard")

    return data

#
#Stack based, uses:
## X = { : key + context open
## } : context close
## X = Y : assignment


if __name__ == "__main__":
    input_ext = [".txt", ".psc", ".ws"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
