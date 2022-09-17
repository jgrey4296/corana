#!/opts/anaconda3/envs/nlp/python
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic
from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir

from code_analysis.util.utils import get_data_files
from bs4 import BeautifulSoup
import networkx as nx

if __name__ == '__main__':
    conversations = get_data_files(join("data", "tyranny", "conversations"),
                                   ext=".conversation")

    # For each conversation,
    # soup it,
    # get each node in the conv
    # construct graph of links, and weight
    # record speakerguid mapping too

    # Save out graph
    # plus draw graph
