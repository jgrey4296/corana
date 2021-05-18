#!/usr/bin/env python3
# TODO sunless sea
import json
import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState


def extract_from_file(filename, ctx):
    data = ParseData(filename)

    obj = None
    with open(filename, 'r') as f:
        obj = json.load(f)



    return data

if __name__ == "__main__":
    input_ext    = [".json"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
