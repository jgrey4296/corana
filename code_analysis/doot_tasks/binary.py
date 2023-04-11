#!/usr/bin/env python3
"""

"""
##-- imports
from __future__ import annotations

import types
import abc
import datetime
import enum
import functools as ftz
import itertools as itz
import logging as logmod
import pathlib as pl
import re
import time
from copy import deepcopy
from dataclasses import InitVar, dataclass, field
from typing import (TYPE_CHECKING, Any, Callable, ClassVar, Final, Generic,
                    Iterable, Iterator, Mapping, Match, MutableMapping,
                    Protocol, Sequence, Tuple, TypeAlias, TypeGuard, TypeVar,
                    cast, final, overload, runtime_checkable)
from uuid import UUID, uuid1
from weakref import ref

##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

import tomler
import doot
from doot import globber

from code_analysis.mixins.dataset_globber import CADatasetGlobber
from code_analysis.structs.binary import infinity

class BiowareInfinityBinaryGlobber(CADatasetGlobber, infinity.BioWareInfinityBinaryMixin):

    select_tags = ["bioware", "infinity"]

    def __init__(self, name="binary::bioware", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], exts=[".key", ".tlk", ".gff", ".d", ".2da"], rec=True)

    def subtask_detail(self, task, fpath):
        match fpath.suffix.lower():
            case ".key":
                parser = self.build_key_v1_format()
            case ".tlk" | ".gff" | ".d" | ".2da":
                logging.debug("Bioware Binary parser not implemented for: %s", fpath)
                return
            case _:
                logging.warn("No Applicable Bioware Binary parser for: %s", fpath)
                return

        task.update({
            "actions" : [ (self.parse_file, [fpath, parser])],
        })
        return task

    def parse_file(self, fpath:pl.Path, parser:Construct.Struct):
        logging.info("-- Binary Parsing File: %s", fpath)
        try:
            result = parser.parse_file(fpath)
        except Exception as err:
            logging.error(f"Binary Parse Failed: %s : %s", fpath, err)

        self.report_resources(result, self.to_mirror(fpath))
        logging.info("-- Binary Parsing Finished: %s", fpath)

    def report_resources(self, data:Construct.Struct, output:pl.Path):
        logging.info("Reporting Results: %s", output)
        assert(all([x in data for x in ["header", "bif_descs", "res_descs"]]))
        select = [0x03ed, 0x03ee, 0x03ef, 0x03f0, 0x03f3, 0x03f4, 0x03f6, 0x03f8, 0x03f9, 0x03fa, 0x03fe, 0x0403, 0x0803]
        header = data.header
        bifs   = data.bif_descs
        recs   = data.res_descs

        results = []
        relevant_bifs = set()
        for res in recs:
            if res.type not in select:
                continue
            bif_name  = bifs[res.index.bif].name.str
            bif_index = res.index.file
            res_name  = res.name
            res_type  = self.file_types.get(res.type)

            relevant_bifs.add(bif_name)
            results.append(f"{bif_name} : {bif_index:<5} : {res_name}{res_type}")

        if not output.parent.exists():
            output.parent.mkdir(parents=True)

        output.with_suffix(".relevant").write_text("\n".join(relevant_bifs))
        output.with_suffix(".resources").write_text("\n".join(results))


