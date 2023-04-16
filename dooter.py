# -*- mode:doot; -*-
"""
Stub dooter file for task authoring

"""
# https://pydoit.org/
##-- imports
from __future__ import annotations
import pathlib as pl
from doit.action import CmdAction
from doit import create_after
from doit.tools import set_trace, Interactive, PythonInteractiveAction
from doit.task import clean_targets

import doot
##-- end imports

from doot.tasks.groups import *
from doot.tasks.groups_secondary import *
from code_analysis.doot_tasks import data_listing, data_toml, data_zip
from code_analysis.doot_tasks import spider as spider_tasks
from code_analysis.doot_tasks import binary

if __name__ == "dooter":
    # the equivalent of main
    data_report    = data_zip.ReportData(locs=doot.locs)
    data_test      = data_zip.ZipCheck(locs=doot.locs)
    unzip_data     = data_zip.UnzipData("zip::extract.raw",     locs=doot.locs, roots=[doot.locs.SD_backup / "raw"], output=doot.locs.raw)
    zip_data       = data_zip.ZipData("zip::compress.raw",      locs=doot.locs, roots=[doot.locs.raw], output=doot.locs.SD_backup / "raw")
    unzip_crawled  = data_zip.UnzipData("zip::extract.crawled", locs=doot.locs, roots=[doot.locs.SD_backup / "crawled"], output=doot.locs.crawled)
    zip_crawled    = data_zip.ZipData("zip::compress.crawled",  locs=doot.locs, roots=[doot.locs.crawled], output=doot.locs.SD_backup / "crawled")

    pop_sum        = data_toml.TomlSummary(locs=doot.locs)
    toml_adjust    = data_toml.TomlAdjust(locs=doot.locs, processor=data_toml.TomlAdjust.adjust_listing)
    toml_zip_hash  = data_toml.TomlAdjust("data::ziphash", locs=doot.locs, processor=data_toml.TomlAdjust.add_zip_hash)
    toml_concat    = data_toml.TomlConcat(locs=doot.locs)
    data_ages      = data_toml.TomlAge(locs=doot.locs)
    data_tagless   = data_toml.TomlTagless(locs=doot.locs)

    run_spider     = spider_tasks.RunSpider(locs=doot.locs)

    bioware_extract = binary.BiowareInfinityBinaryGlobber("binary::bioware.extract", locs=doot.locs, roots=[doot.locs.data / "raw"], exts=[".key", ".bif", ".tlk"], result_tag="binary")
    bioware_parse   = binary.BiowareInfinityBinaryGlobber("binary::bioware.parse",   locs=doot.locs, roots=[doot.locs.data / "binary"], exts=[".dlg"], result_tag="parsed")
