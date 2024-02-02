#!/usr/bin/env python3

##-- imports
import pathlib as pl
from importlib.resources import files
##-- end imports

__all__ = [
    "load_orig"
]

data_path = files("corana.__data.originals")

def load_orig(*paths) -> list[pl.Path]:
    """
    Get a bunch of data
    last arg can be a `*.ext` to dfs all files below cwd
    """
    current = data_path
    for folder in paths[:-1]:
        current = current / folder

    if (current / paths[-1]).exists():
        # Just a single path
        return [(current /paths[-1])]

    # Else dfs for everything
    found = []
    queue = [current]
    while bool(queue):
        cwd = queue.pop()

        if cwd.is_file() and cwd.suffix == paths[-1]:
            found.append(cwd)
        elif cwd.is_dir():
            queue += cwd.iterdir()

    return found
