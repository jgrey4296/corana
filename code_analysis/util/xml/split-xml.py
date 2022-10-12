#/usr/bin/env python3
"""

"""
##-- imports
from __future__ import annotations

import abc
import argparse
import logging as logmod
import copy
import re
import pathlib
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from re import Pattern
from sys import stderr, stdout
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable)
from uuid import UUID, uuid1
from weakref import ref

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    # tc only imports
    pass
##-- end imports

##-- argparse
#see https://docs.python.org/3/howto/argparse.html
argparser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog = "\n".join([""]))
argparser.add_argument("-v", "--verbose",     action='count', help="increase verbosity of logging (repeatable)")
argparser.add_argument('--logfilter')
argparser.add_argument('-t', '--target')
argparser.add_argument('-o', '--output')
argparser.add_argument('-f', '--first', action="append")
argparser.add_argument('-s', '--split', action="append")

args = argparser.parse_args()
##-- end argparse

##-- Logging
DISPLAY_LEVEL = logmod.DEBUG
LOG_FILE_NAME = "log.{}".format(pathlib.Path(__file__).stem)
LOG_FORMAT    = "%(asctime)s | %(levelname)8s | %(message)s"
FILE_MODE     = "w"
STREAM_TARGET = stderr # or stdout

logging         = logmod.root
logging.setLevel(logmod.NOTSET)
console_handler = logmod.StreamHandler(STREAM_TARGET)
file_handler    = logmod.FileHandler(LOG_FILE_NAME, mode=FILE_MODE)

console_handler.setLevel(DISPLAY_LEVEL)
# console_handler.setFormatter(logmod.Formatter(LOG_FORMAT))
file_handler.setLevel(logmod.DEBUG)
# file_handler.setFormatter(logmod.Formatter(LOG_FORMAT))

logging.addHandler(console_handler)
logging.addHandler(file_handler)

verbosity = max(logmod.DEBUG, logmod.WARNING - (10 * (args.verbose or 0)))
console_handler.setLevel(verbosity)
if args.logfilter:
    console_handler.addFilter(logmod.Filter(args.logfilter))
##-- end Logging

remove_re = re.compile(r"[,'\\\/():-]")
flat_re   = re.compile(r'[\s\.]+')

def process_target(target, output, first, split):
    logging.info("Processing: %s", target)
    with open(target, 'r') as f:
        soup = BeautifulSoup(f.read(), features="xml")

    assert(soup is not None)

    groups = []
    logging.info("There are %s tags found for %s", len(soup.find_all(first)), first)
    for heading in soup.find_all(first):
        group = BeautifulSoup('<xml/>', features='xml')
        group.xml.append(copy.copy(heading))

        current = heading.next_sibling
        while current is not None and current.name not in  split:
            group.xml.append(copy.copy(current))
            current = current.next_sibling

        logging.debug("Found Group of length: %s", len(group))
        groups.append(group)


    for group in groups:
        head = group.xml.contents[0].h2.a
        head_str = flat_re.sub('_', remove_re.sub('', head.name + "_" + head.get_text()))
        while (output / f"{head_str}.xml").exists():
            head_str += "_d"

        logging.info("Writing out: %s", head_str)
        prettified = group.prettify(formatter='minimal')
        with open(output / f"{head_str}.xml", 'w') as f:
            f.write(prettified)



def main():
    target = pathlib.Path(args.target).expanduser().resolve()
    output = pathlib.Path(args.output).expanduser().resolve()

    logging.info("Loading: %s", target)
    logging.info("Output: %s", output)

    if not output.exists():
        output.mkdir()

    assert(output.is_dir())

    targets = []
    if target.is_dir():
        targets = [x for x in target.iterdir() if x.suffix == ".xml"]
    else:
        targets = [target]

    for t in targets:
        process_target(t, output, args.first, args.split)


if __name__ == '__main__':
    main()
