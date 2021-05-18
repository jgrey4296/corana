#!/usr/bin/env python3
# TODO
# needs to load txt, lua, xml
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState

import handle_txt
import handle_lua
import handle_xml

def extract_from_file(filename, ctx):
    data = ParseData(filename)
    file_ext = splitext(filename)[1]

    if file_ext == ".txt":
        handle_txt.handle_txt(data, filename)
    elif file_ext == ".lua":
        handle_lua.handle_lua(data, filename)
    elif file_ext == ".xml":
        handle_xml.handle_xml(data, filename)
    else:
        logging.warning("Unrecognized file type")
        data.flag("discard")

    return data


if __name__ == "__main__":
    input_ext    = [".txt", ".lua", ".xml"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
