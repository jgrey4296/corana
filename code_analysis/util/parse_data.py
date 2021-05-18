#!/usr/bin/env python3
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

import json
from collections import defaultdict
from uuid import UUID
import logging as root_logger
logging = root_logger.getLogger(__name__)

from dataclasses import dataclass, field, InitVar

from code_analysis.util.parse_base import ParseBase

subgroup_default = lambda: defaultdict(lambda: set())
count_default = lambda: defaultdict(lambda: 0)

UUIDstr = str

@dataclass
class ParseData:
    """ Aggregate parse data """
    source_file   : str                       = field()
    flags         : Set[str]                  = field(default_factory=set)
    misc          : Dict[str, Any]            = field(default_factory=dict)

    # Counts:
    counts        : Dict[str, int]            = field(init=False, default_factory=count_default)
    # Elements:
    strings       : List[Any]                 = field(init=False, default_factory=list)
    subgroups     : Dict[str, Set[UUIDstr]]   = field(init=False, default_factory=subgroup_default)
    ordered       : List[Tuple[UUIDstr, int]] = field(init=False, default_factory=list)
    total         : Dict[UUIDstr, ParseBase]  = field(init=False, default_factory=dict)

    def inc_comment(self):
        self.counts["comments"] += 1

    def insert(self, element: ParseBase, *args):
        if element is None:
            return

        str_uuid = str(element.uuid)
        if str_uuid not in self.total and element.line_no != -1:
            self.ordered.append((str_uuid, element.line_no))

        all_components = element.flatten()
        all_comp_uuids = [str(x.uuid) for x in all_components]
        self.total.update({str(x.uuid) : x for x in all_components})

        for x in args:
            self.subgroups[x].update(all_comp_uuids)

    def count(self, **kwargs):
        for k,v in kwargs.items():
            self.counts[k] += v

    def dumps(self):
        """ Return an output format representation of the object """
        ordered   = sorted(self.ordered, key=lambda x: x[1])
        total     = [x.to_dict() for x in self.total.values()]
        subgroups = {x: list(y) for x,y in self.subgroups.items()}

        return json.dumps({"counts"    : self.counts,
                           "strings"   : self.strings,
                           "subgroups" : subgroups,
                           "ordered"   : ordered,
                           "total"     : total,
                           "flags"     : list(self.flags),
                           "source_file" : self.source_file},
                          indent=4)

    def flag(self, *args):
        self.flags.update(args)
