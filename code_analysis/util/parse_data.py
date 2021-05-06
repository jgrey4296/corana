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

subgroup_default = defaultdict(lambda: [])
count_default = defaultdict(lambda: 0)

@dataclass
class ParseData:
    """ Aggregate parse data """

    # Counts:
    counts        : Dict[Any, int]         = field(init=False, default_factory=count_default)
    # Elements:
    strings       : List[Any]              = field(init=False, default_factory=list)
    subgroups     : Dict[str, List[str]]         = field(init=False, default_factory=subgroup_default)
    ordered       : List[Tuple[str, int]] = field(init=False, default_factory=list)
    total         : Dict[str, ParseBase]  = field(init=False, default_factor=dict)

    def inc_comment(self):
        self.counts["comments"] += 1

    def insert(self, element: ParseBase, *args):
        str_uuid = str(element.uuid)
        if str_uuid not in total:
            self.total[str_uuid] = element
            self.in_order.append((str_uuid, element.line_no))

        for x in args:
            if str_uuid not in self.subgroups[x]:
                self.subgroups[x].append(str_uuid)

    def count(self, **kwargs):
        for k,v in kwargs:
            self.counts[k] += v

    def dumps(self):
        """ Return an output format representation of the object """
        ordered   = json.dumps(sorted(self.ordered, key=lambda x: x[1]))
        total     = [x.dumps() for x in self.total.values()]

        return json.dumps({"counts"    : self.counts,
                           "strings"   : self.strings,
                           "subgroups" : self.subgroups,
                           "ordered"   : ordered,
                           "total"     : total},
                          indent=4)
