#!/usr/bin/env python3

import code_analysis.util.post_processor as PP
from code_analysis.util.parse_base import ParseBase
from code_analysis.util.parse_data import ParseData
from code_analysis.util.parse_state import ParseState


def post_process_file(data, ctx):
    result = None

    return result


if __name__ == "__main__":

    PP.PostProcessor(__file__,
                     post_process_file)()
