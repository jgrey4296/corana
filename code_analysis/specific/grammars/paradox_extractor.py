
import argparse
import json
import logging as root_logger
import re
from os import listdir
from os.path import (abspath, exists, expanduser, isdir, isfile, join, split,
                     splitext)

import pyparsing as pp

LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################

#see https://docs.python.org/3/howto/argparse.html
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog = "\n".join([""]))
parser.add_argument('--aBool', action="store_true")

if __name__ == '__main__':
    args = parser.parse_args()


    with open(args.target, 'r') as f:
        lines = f.readlines()


    obj_stack = [data]
    accumulated = ""

    while bool(lines):
        current = lines.pop(0)

        if current.strip() == "":
            continue

        if re.match("^\s*#", current):
            continue

        if re.match("\s+ = {\s*}$", current):
            continue

        match = re.search("(\w+) = {$", current):
        if match:
            new_obj = {}
            obj_stack[-1][match[1]] = new_obj
            obj_stack.append(new_obj)
            continue

        if re.match("}", current):
            obj_stack[-1]['value'] = accumulated
            accumulated = ""
            obj_stack.pop()


        match = re.search("(\w+) = (.+?)", current):
        if match:
            obj_stack[-1][match[1]] = match[2]
