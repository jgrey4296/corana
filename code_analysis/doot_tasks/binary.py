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

from collections import defaultdict
import doot
from doot import globber

from code_analysis.mixins.dataset_globber import CADatasetGlobber
from code_analysis.structs.binary import infinity

class BiowareInfinityBinaryGlobber(CADatasetGlobber, infinity.BioWareInfinityBinaryMixin):
    """
    extract files from infinity engine .bif 's, and parse them
    """

    select_tags    = ["bioware", "infinity_engine"]
    select_types   = [0x03ed, 0x03ee, 0x03ef, 0x03f0, 0x03f3, 0x03f4, 0x03f6, 0x03f8, 0x03f9, 0x03fa, 0x03fe, 0x0403, 0x0803]
    needs_key_file = [".bif"]

    def __init__(self, name="binary::bioware", locs=None, roots=None, exts=None, result_tag="binary"):
        super().__init__(name, locs, roots or [locs.data], exts=exts or [".key", ".bif", ".tlk", ".gff", ".dlg", ".2da"], rec=True)
        self.current_key_file             = None
        self.resource_desc_lookup = dict()
        self.result_tag           = result_tag

    def subtask_detail(self, task, fpath):
        parser      = None
        handlers    = []
        marker      = self.find_marker(fpath)
        match fpath.suffix.lower():
            case ".key":
                parser  = self.build_key_v1_format()
                handlers.append(self.report_resources)
                handlers.append(self.setup_key_lookup)
            case ".bif":
                parser   = self.build_bif_v1_format()
                handlers.append(self.write_bif_contents)
            case ".dlg":
                parser   = self.build_dlg_v1_format()
                handlers.append(self.write_dlg_contents)
            case ".tlk":
                parser = self.build_tlk_v1_format()
                handlers.append(self.write_tlk_contents)
            case ".tlk" | ".gff" | ".2da":
                logging.debug("Bioware Binary parser not implemented for: %s", fpath)
                return
            case _:
                logging.warn("No Applicable Bioware Binary parser for: %s", fpath)
                return

        task.update({
            "actions" : [
                (self.make_linked_dataset, [self.result_tag, fpath]), # -> dataset
                (self.find_key, [fpath]),
                (self.parse_file, [fpath, parser, handlers]),
                ],
        })
        return task

    def find_key(self, fpath):
        if fpath.suffix.lower() not in self.needs_key_file:
            return

        marker = self.find_marker(fpath)
        if marker is None:
            raise FileNotFoundError(f"Can't find dataset marker for: {fpath}")

        keys    = list(marker.parent.rglob("*.key"))
        if bool(keys) and keys[0] != self.current_key_file:
            self.parse_file(keys[0], self.build_key_v1_format(), [self.setup_key_lookup])
            self.current_key_file = keys[0]
            return
        elif bool(keys) and keys[0] == self.current_key_file:
            return

        logging.warning("Can't Find a key file for: %s", fpath)
        return False

    def parse_file(self, fpath:pl.Path, parser:Construct.Struct, handlers:list[Callable]):
        try:
            logging.info("-- Binary Parsing File: %s", fpath)
            result = parser.parse_file(fpath)
            logging.info("-- Binary Parsing Finished: %s", fpath)
            for handler in handlers:
                handler(fpath, result)
        except Exception as err:
            logging.error(f"-- Binary Parse Failed: %s : %s", fpath, err)
            raise err from err

    def report_resources(self, fpath, data:Construct.Struct):
        output = self.to_linked_data_path(fpath.parent, self.result_tag)
        logging.info("Reporting Results to: %s", output)
        assert(all([x in data for x in ["header", "bif_descs", "res_descs"]]))
        header = data.header
        bifs   = data.bif_descs
        recs   = data.res_descs

        results       = []
        relevant_bifs = set()
        for res in recs:
            res_key  = res.resource_key
            bif_name = bifs[res.resource_key.bif].name
            bif_key  = res.resource_key.file
            res_name = res.name
            res_type = self.file_types.get(res.type)
            results.append(f"{bif_name} : {res_key.bif}_{res_key.tile}_{res_key.file} : {res_name}{res_type}")

            if res.type not in self.select_types:
                relevant_bifs.add(bif_name)
                continue

        (output / "key.relevant").write_text("\n".join(relevant_bifs))
        (output / "key.resources").write_text("\n".join(results))

    def setup_key_lookup(self, fpath, data):
        header = data.header
        recs   = data.res_descs
        bifs   = data.bif_descs
        for res in recs:
            res_key  = res.resource_key
            bif_name = pl.Path(bifs[res.resource_key.bif].name).stem.lower()
            res_name = res.name
            res_type = self.file_types.get(res.type)
            self.resource_desc_lookup[f"{bif_name}_{res_key.file}".lower()] = f"{res_name}{res_type}"

    def write_bif_contents(self, fpath, data):
        output = self.to_linked_data_path(fpath.with_suffix(""), self.result_tag)
        logging.info("-- Writing Raw Bif Contents: %s : %s", data.header.file_entries_count, output)
        for entry in data.file_entries:
            key = entry.resource_key

            true_name = self.resource_desc_lookup.get(f"{fpath.stem}_{key.file}".lower(), None)
            if true_name is None:
                logging.warning("Resource Not Found in key resources: %s : %s : %s", key.bif, key.tile, key.file)
                true_name = f"{fpath.stem}_{key.file}.raw"

            (output / true_name).write_bytes(bytes(entry.data))

    def write_dlg_contents(self, fpath, data):
        output = self.to_linked_data_path(fpath.with_suffix(""), self.result_tag)
        logging.info("-- Writing Raw DLG Contents: %s : %s", fpath, output)
        logging.info("State Count: %s", data.header.state_count)
        logging.info("Transition Count: %s", data.header.transition_count)
        logging.info("State Trigger Count: %s", data.header.state_trigger_count)
        logging.info("Transition Trigger Count: %s", data.header.transition_trigger_count)
        logging.info("Action Count: %s", data.header.action_count)

    def write_tlk_contents(self, fpath, data):
        logging.info("Parsed TLK")
        logging.info("Lang: %s", data.header.language)
        logging.info("Entries: %s", data.header.entry_count)
