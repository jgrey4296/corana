#!/usr/bin/env python3

from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir


#https://docs.python.org/3/library/dataclasses.html
from dataclasses import dataclass, field, InitVar

@dataclass
class PostProcessor:
    """
    Read analysis files and produce aggregate information
    """

    root      : str
    processor : Callable

    _analysis_dir : str = field(init=False)
    _out_dir      : str = field(init=False)

    def __post_init__(self, other):
        self._analysis_dir = join(dirname(self.root), "analysis")
        self._out_dir      = join(dirname(self.root), "post_analysis")

        # if outdir doesn't exist, create it

    def __call__(self):
        # find files

        # read in

        # reconstruct parse objects

        # process

        # output
        pass

    def _output(self, data):
        pass
