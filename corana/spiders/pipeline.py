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

from urllib.parse import urlparse
import json
from bs4 import BeautifulSoup
import datetime

class CrawlSingleItemXMLExporter:
    """
    """

    def open_spider(self, spider):
        logging.debug("Opened CrawlXMLExporter")
        self.base = spider.task.data_dir

    def close_spider(self, spider):
        logging.debug("Closed CrawlXMLExporter")
        pass

    def process_item(self, item, spider):
        logging.debug("Exporting Item: %s", item.get('source_url', "Unknown"))
        soup                        = BeautifulSoup("<items/>", features="lxml-xml")
        soup.items['source_url']     = item.get('source_url', "Unknown")
        soup.items['parse_date']     = datetime.datetime.now().isoformat()
        soup.items['needs_subsplit'] = item.get('needs_subsplit', False)

        data_soup = BeautifulSoup("\n".join(item.get('data', [])), features="lxml-html")
        data_soup.body.wrap(data_soup.new_tag("item"))
        data_soup.html.unwrap()
        data_soup.body.unwrap()
        soup.item.append(data_soup)

        name     = urlparse(item['source_url']).path.replace("/","_")
        (self.base / name).with_suffix(".xml").write_text(soup.prettify())

        return item


class CrawlMultiItemXMLExporter:
    """
    """

    def open_spider(self, spider):
        logging.debug("Opened CrawlXMLExporter")
        self.base = spider.task.data_dir

    def close_spider(self, spider):
        logging.debug("Closed CrawlXMLExporter")
        pass

    def process_item(self, item, spider):
        logging.debug("Exporting Item: %s", item.get('source_url', "Unknown"))
        soup                        = BeautifulSoup("<items/>", features="lxml-xml")
        soup.items['source_url']     = item.get('source_url', "Unknown")
        soup.items['parse_date']     = datetime.datetime.now().isoformat()
        soup.items['needs_subsplit'] = item.get('needs_subsplit', False)

        for subitem in item.get('data', []):
            data_soup = BeautifulSoup(subitem, features="lxml-html")
            data_soup.body.wrap(data_soup.new_tag("item"))
            data_soup.body.unwrap()
            data_soup.html.unwrap()
            soup.items.append(data_soup)

        name     = urlparse(item['source_url']).path.replace("/","_")
        (self.base / name).with_suffix(".xml").write_text(soup.prettify())

        return item
