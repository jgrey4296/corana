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

import re
import fileinput
import datetime
import zlib
import ast
import hashlib
from doot import tasker, globber, task_mixins
from doot.taskslib.groups import *
from doot.taskslib.groups_secondary import *
from doot.taskslib.files import listing
from doot.taskslib.files.backup import BackupTask

zip_marker = doot.config.on_fail(".zipthis.toml", str).tool.doot.zipper.marker()


class PopulateSummaries(globber.DirGlobMixin, globber.DootEagerGlobber, task_mixins.ActionsMixin):
    """
    Find all zip markers, and add the basic toml structure for them
    """

    def __init__(self, name="data::tomlise", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)

    def filter(self, fpath):
        if (fpath / zip_marker).exists():
            return self.control.keep
        return self.control.discard

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [
                (self.prepare_toml, [fpath]),
            ]
        })
        return task

    def prepare_toml(self, fpath) :
        existing_text : str           = (fpath / zip_marker).read_text().strip()
        files         : list[pl.Path] = [f.relative_to(fpath) for f in fpath.rglob("*") if f.is_file() and f.name not in (zip_marker, ".DS_Store")]
        exts          : set[str]      = set(f"\"{x.suffix}\"" for x in files if bool(x.suffix))
        toml_lines    : list[str]     = []
        now           : str           = datetime.datetime.now().isoformat()

        toml_lines.append("[dataset] # A Data Summary for integrity")
        toml_lines.append(f"name         = \"{fpath.stem}\" # A Name to refer to this data. Default: directory name")
        toml_lines.append("tags          = [] # Tags to collect different datasets together")
        toml_lines.append("source        = [] # Where its from")
        toml_lines.append(f"count         = {len(files)} # Number of files in dataset")
        toml_lines.append("file_types    = [ " + ", ".join(exts) + " ] # Extensions of files in dataset")
        toml_lines.append("")
        toml_lines.append("# Every single file below this summary in the dataset")
        toml_lines.append("listing       = [ " + ", ".join(f"\"{x}\"" for x in files) + " ]")
        toml_lines.append("data-zip-hash = \"TODO\" # md5 hash of the files in listing zipped together")
        toml_lines.append("")
        toml_lines.append(f"[dataset.log] # Recording things done to this data")
        toml_lines.append(f"initial-date = \"{now}\" # When this summary was created")
        toml_lines.append("preprocessing = [] # Things done to data before it was added")
        toml_lines.append("")
        toml_lines.append("# Subgroups of the files of particular interest")
        toml_lines.append("[[dataset.subgroup]]")

        toml_lines.append("# Additional")
        toml_lines.append(existing_text)
        text = "\n".join(toml_lines)
        self.verify_toml(text)
        (fpath / zip_marker).write_text(text)

    def verify_toml(self, text):
        # TODO
        pass

class ZipData(globber.DirGlobMixin, globber.DootEagerGlobber, task_mixins.ZipperMixin, task_mixins.ActionsMixin):

    def __init__(self, name="zip::code", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True)
        self.output = locs.backup

    def filter(self, fpath):
        if (fpath / zip_marker).exists():
            return self.control.keep
        return self.control.discard

    def subtask_detail(self, task, fpath):
        target_path = self.calc_zip_path(fpath)
        task.update({
            "actions": [
                (self.mkdirs, [target_path.parent]),
                (self.zip_set_root, [fpath]),
                (self.zip_create, [target_path]),
                (self.zip_globs, [target_path, str(fpath / "**/*")]),
            ],
        })
        return task

    def calc_zip_path(self, fpath):
        root = self.locs.data
        base = self.output / fpath.relative_to(root).with_suffix(".zip")
        return base






class TomlConcat(globber.DootEagerGlobber):
    """
    Combine all zip_markers
    """

    def __init__(self, name="data::concat", locs=None, roots=None):
        super().__init__(name, locs, roots or [locs.data], rec=True, exts=[".toml"])
        self.output = locs.build / "datasets.toml"

    def filter(self, fpath):
        if fpath.name == zip_marker:
            return self.control.keep
        return self.control.discard

    def subtask_detail(self, task, fpath):
        task.update({
            "actions" : [ (self.append_dataset, [fpath]) ],
        })
        return task

    def append_dataset(self, fpath):
        data = fpath.read_text()
        with open(self.output, 'a') as f:
            f.write(f"\n#-------------------- {fpath} \n")
            f.write("[[dataset]]\n")
            f.write(data)



class TomlAdjust(tasker.DootTasker):

    def __init__(self, name="data::adjust", locs=None):
        super().__init__(name, locs)
        self.dataset_re = re.compile(r"^\[dataset\]")
        self.listing_re = re.compile(r"^listing\s+=\s+(\[.+?\])")
        self.hash_re    = re.compile(r"^data-zip-hash")

    def task_detail(self, task):
        task.update({
            "actions": [ (self.adjust_tomls, [self.add_zip_hash])],
        })
        return task

    def adjust_tomls(self, processor):
        globbed = list(self.locs.data.rglob(zip_marker))
        if not bool(globbed):
            return
        print(f"Found {len(globbed)} files")

        for line in fileinput.input(files=globbed, inplace=True):
            if not processor(line):
                print(line, end="")

    def adjust_head(self):
        if not self.dataset_re.match(line):
            return False

        print("[dataset.instance] # A Data Summary for Integrity")
        return True

    def adjust_listing(self):
        raise Exception()
        maybe_match = self.listing_re.match(line)
        if not maybe_match:
            return False

        compressed = str(zlib.compress(maybe_match[1].encode()))
        print(line, end="")
        print("# Zlib Compressed File Listing, decompress with python json.loads(zlib.decompress(ast.literal_eval($)))")
        print(f"compressed_listing = \"{compressed}\"")
        return True


    def add_zip_hash(self, line):
        maybe_match = self.hash_re.match(line)
        if not maybe_match:
            return False

        filename =  pl.Path(fileinput.filename()).parent.relative_to(self.locs.data).with_suffix(".zip")
        target = self.locs.backup / filename
        assert(target.exists()), target
        with open(target, 'rb') as f:
            digest = hashlib.file_digest(f, "sha256").hexdigest()

        print(f"data-zip-sha256 = \"{digest}\"")
        return True

if __name__ == "dooter":
    # the equivalent of main
    simple_listing = listing.SimpleListing("listing::originals", locs=doot.locs, focus=doot.locs.data / "originals")
    zip_data       = ZipData(locs=doot.locs)
    pop_sum        = PopulateSummaries(locs=doot.locs)
    toml_adjust    = TomlAdjust(locs=doot.locs)
    toml_concat    = TomlConcat(locs=doot.locs)
    backup_zips    = BackupTask("backup::zips", locs=doot.locs, roots=[doot.locs.backup], output=doot.locs.SD_backup)
