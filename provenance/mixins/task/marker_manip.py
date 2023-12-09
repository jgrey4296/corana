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
from importlib.resources import files
##-- end imports

##-- logging
logging = logmod.getLogger(__name__)
##-- end logging

from os.path import commonpath
import tomlguard as TG
from string import Template
import doot

##-- data
data_path = files("provenance.__data")
data_file = data_path.joinpath("zip_marker_template")
dataset_marker_template : Final[Template] = Template(data_file.read_text())
##-- end data

dataset_marker = doot.config.on_fail(".zipthis.toml", str).dataset.marker()

class MarkerManipulationMixin:

    def make_new_dataset(self, tag:str, name:str):
        """
        make a new dataset at data / tag / name
        """
        fpath = self.locs.data / tag / name
        if fpath.exists():
            raise FileExistsError(f"Dataset already exists: {fpath}")

        fpath.mkdir(parents=True)

        (fpath / dataset_marker).touch()
        self.make_marker(fpath)
        return { "dataset" : fpath }

    def make_linked_dataset(self, tag, fpath):
        """
        make a new dataset, linked to the dataset fpath is part of
        """
        marker = self.find_marker(fpath)
        fpath  = self.locs.data / tag / marker.parent.name
        if fpath.exists() and (fpath / dataset_marker).exists():
            logging.debug("Dataset link already exists: %s", fpath)
            return { "dataset" : str(fpath) }

        fpath.mkdir(parents=True, exist_ok=True)
        (fpath / dataset_marker).hardlink_to(marker)
        # TODO add dataset subgroup to marker

        return { "dataset" : str(fpath) }

    def find_marker(self, fpath) -> None|pl.Path:
        if fpath.name == dataset_marker:
            return fpath

        if (fpath / dataset_marker).exists():
            return fpath / dataset_marker

        for parent in fpath.parents:
            if (parent / dataset_marker).exists():
                return parent / dataset_marker

        return None

    def make_marker(self, fpath, skip_existing=False):
        logging.info(f"Preparing Dataset Toml: {fpath}")
        marker        : None|pl.Path = self.find_marker(fpath)

        existing_text : list[str]    = []
        match marker:
            case None:
                target_dir  = fpath if fpath.is_dir() else fpath.parent()
                marker      = target_dir / dataset_marker
            case pl.Path() if skip_existing:
                logging.debug("Marker exists, skipping: %s", marker)
                return
            case pl.Path():
                text          : str       = marker.read_text().strip()
                existing_text : list[str] = [f"\"{x.strip()}\"" for x in text.split("\n") if bool(x.strip())]

        logging.debug("Target Marker to Create: %s", marker)
        files      : list[pl.Path] = list(fpath.rglob("*"))
        exts       : set[str]      = set(f"\"{x.suffix}\"" for x in files if bool(x.suffix))
        now        : str           = datetime.datetime.now().isoformat()

        text = zip_marker_template.substitute(name=fpath.stem,
                                              count=len(files),
                                              exts=" ".join(exts),
                                              date=now,
                                              notes="\n".join(existing_text)
                                              )

        if self.verify_toml(text):
            marker.write_text(text)
            return {'marker' : marker }
        else:
            logging.error("Marker Doesn't verify: %s", marker)
            return False

    def verify_toml(self, text) -> bool:
        try:
            data = TG.read(text)
            return True
        except Exception as err:
            logging.error("TOML text failed to parse: %s", err)
            return False

    def is_marker_tagged(self, fpath:None|pl.Path, *tags) -> bool:
        if fpath is None:
            return False

        assert(fpath.exists())
        data = TG.load(fpath)
        toml_tags = data.on_fail([], list).dataset.instance.tags()
        return not bool(tags) or all([x in toml_tags for x in tags])

    def to_linked_data_path(self, fpath:pl.Path, tag="_basic"):
        """
        mirror the given path to a different root
        """
        marker       = self.find_marker(fpath)
        if marker is None:
            raise FileNotFoundError(f"Can't mirror data without a dataset marker: {fpath}")

        rel_path     = fpath.relative_to(marker.parent)

        mirrored = self.locs.data / tag / marker.parent.name / rel_path
        if self.find_marker(mirrored) is None:
            raise FileNotFoundError(f"Mirrored Datatset hasn't been initialised: {mirroed}")

        if mirrored.is_file():
            mirrored.parent.mkdir(parents=True, exist_ok=True)
        else:
            mirrored.mkdir(parents=True, exist_ok=True)

        return mirrored
