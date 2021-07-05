#!/usr/bin/env python3
# TODO
# needs to handle txt
#

import code_analysis.util.analysis_case as AC
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState


def extract_from_file(filename, ctx):
    data = ParseData(filename)

    lines = []
    with open(filename, 'r') as f:
        lines = f.readlines()


    return data


if __name__ == "__main__":
    input_ext    = [".txt"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
