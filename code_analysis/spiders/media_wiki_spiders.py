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

from doot.spiders.spiders import DootBasicSpider

class MediaWikiSpider(DootBasicSpider):

    def parse_mw_link_page(self, response):
        pass

    def parse_mw_multi_page(self, response):
        yield from response.follow_all(xpath="//a[contains(text(), 'next page')]", callback=self.parse_mw_multi_page)
        yield from response.follow_all(response.css(".mw-category").xpath(".//a/@href").get_all(), callback=self.parse_mw_multi_page)
        yield from response.follow_all(response.css("#mw-pages").xpath(".//a/@href").get_all(), callback=self.parse_mw_content_page)

    def parse_mw_content_page(self, response):
        data = response.css(".mw-parser-output").get()
        yield {
            "source_url"     : response.url,
            "data"           : data,
            "needs_subsplit" : True,
        }

    def parse_mw_content_grouped(self, response):
        current_data = []
        # Group by h2's
        for item in response.css(".mw-parser-output").xpath("./*"):
            if bool(item.xpath("self::node()[self::h2]")) and bool(current_data):
                grouped      = current_data[:]
                current_data = []
                yield {
                    "source_url": response.url,
                    "data" : grouped,
                    "needs_subsplit": True,
                }

            current_data.append(item.get())

        if bool(curent_data):
            grouped      = current_data[:]
            current_data = []
            yield {
                "source_url": response.url,
                "data" : grouped,
                "needs_subsplit": True,
            }


class DwarfFortressWikiSpider(MediaWikiSpider):

    def parse(self, response):
        links = response.xpath("//a/@href").re(r".+?Release_information/[.0-9a-m]+")
        yield from response.follow_all(links, callback=self.parse_mw_content_page)


class QudWikiSpider(MediaWikiSpider):

    def parse(self, response):
        yield from response.follow_all(xpath="//a[contains(@title, 'Version')]/@href", callback=self.parse_mw_content_page)


class ParadoxWikiSpider(MediaWikiSpider):

    def parse(self, response):
        links = response.css(".mw-parser-output").css("table").css("a::attr(href)").re(".+Patch.+")
        yield from response.follow_all(links, callback=self.parse_mw_content_page)

class WowPediaSpider(MediaWikiSpider):

    def parse(self, response):
        yield from self.parse_mw_multi_page(response)


class RimworldWikiSpider(MediaWikiSpider):

    def parse(self, response):
        yield from self.parse_mw_multi_page(response)


class TF2WikiSpider(MediaWikiSpider):

    def parse(self, response):
        yield from response.follow_all(xpath="//a[contains(text(), 'next page')]/", callback=self.parse_tf2)
        yield from response.follow_all(xpath="//ul/li/a[contains(text(), 'Patch')]/@href", callback=self.parse_mw_content_page)


class OxygenNotIncludedSpider(MediaWikiSpider):

    def parse(self, response):
        links = response.css(".mw-parser-output").xpath(".//a/@href").getall()
        yield from response.follow_all(links, callback=self.parse_mw_content_page)


class SimsWikiSpider(MediaWikiSpider):

    def parse(self, response):
        yield response.follow(css=".category-page__pagination-next", callback=self.parse_sims)
        patches = response.css(".category-page__members").xpath(".//a[contains(text(), 'Patch')]").getall()
        yield from response.follow_all(patches, callback=self.parse_mw_content_page)


class StardewWikiSpider(MediaWikiSpider):

    def parse(self, response):
        yield from self.parse_content_grouped(self, response)


class DotaWikiSpider(MediaWikiSpider):

    def parse(self, response):
        links = response.css(".mw-parser-output").xpath(".//a[contains(@href, 'wiki')]").getall()
        yield from response.follow_all(links, callback=self.parse_mw_content_page)


class ZeroPunctuationSpider(MediaWikiSpider):

    def parse(self, response):
        links = response.css(".mw-parser-output").css(".wikitable").xpath(".//a[contains(@href, 'wiki')]/@href").getall()
        logging.info("Found %s links", len(links))
        yield from response.follow_all(links, callback=self.parse_zero_punctuation, dont_filter=True)

    def parse_zero_punctuation(self ,response):
        logging.info("Parsing video response")
        data = []
        for item in response.css(".mw-parser-output").xpath("./*"):
            if not bool(data) and item.xpath("self::node()[not(self::h2)]"):
                continue
            elif bool(data) and item.xpath("self::node()[self::h2]"):
                break
            else:
                data.append(item.get())

        logging.info("Yielding data for: %s", response.url)
        yield {
            "source_url"     : response.url,
            "data"           : data,
            "needs_subsplit" : True
        }



class ArcenWikiSpider(MediaWikiSpider):

    def parse(self, response):
        yield from self.parse_mw_multi_page(response)
