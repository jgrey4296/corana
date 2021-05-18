#!/usr/bin/env python3
# TODO
import sqlite3

def extract_from_file(filename, ctx):
    data = ParseData(filename)

    # TODO connect to sqlite database

    return data


if __name__ == "__main__":
    input_ext    = [".sql"]

    AC.AnalysisCase(__file__,
                    input_ext,
                    extract_from_file)()
