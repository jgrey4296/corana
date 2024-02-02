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
import scrapy
import json

class FacebookPolicySpider(DootBasicSpider):

    def parse(self, response):
        policies = response.xpath("//a/@href").re("policies.community-standards..+")
        for link in policies;
            yield from response.follow_all(link, callback=self.parse_facebook_policy)

    def parse_facebook_policy(self, response):
        curl_request = "curl 'https://transparency.fb.com/async/change_log/content/' -X POST -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/110.0' -H 'Accept: */*' -H 'Accept-Language: en-GB,en;q=0.5' -H 'Accept-Encoding: gzip, deflate, br' -H 'Referer: https://transparency.fb.com/en-gb/policies/community-standards/violence-incitement/' -H 'Content-Type: application/x-www-form-urlencoded' -H 'X-FB-LSD: _pxAU1TVQ0T0qCO7WA5ZR6' -H 'X-ASBD-ID: 198387' -H 'Origin: https://transparency.fb.com' -H 'DNT: 1' -H 'Alt-Used: transparency.fb.com' -H 'Connection: keep-alive' -H 'Cookie: cb=3_2023_03_04_' -H 'Sec-Fetch-Dest: empty' -H 'Sec-Fetch-Mode: cors' -H 'Sec-Fetch-Site: same-origin' -H 'Sec-GPC: 1' -H 'Pragma: no-cache' -H 'Cache-Control: no-cache' --data-raw 'cms_id={}&__user=0&__a=1&__dyn=7xe6E5aQ1PyUbFuC1swgE98nwgU6C7UW3q327E2vwXw5ux60Vo1upE4W0OE2WxO0FE2aw7BKdwnU1e42C220qu0ny0RE2Jw8W1uwc-0pa0h-0Lo6-0iq&__csr=&__req=o&__hs=19425.BP%3ADEFAULT.2.0.0.0.0&dpr=1&__ccg=UNKNOWN&__rev=1007081754&__s=lrqoq2%3A16f2x4%3Ag5dzbs&__hsi=7208571118460813206&__comet_req=0&lsd=_pxAU1TVQ0T0qCO7WA5ZR6&jazoest=21702&__spin_r=1007081754&__spin_b=trunk&__spin_t=1678376253'"
        try:
            cms_ids = json.loads("{{ {} }}".format(response.css("body").re("\"cms_ids\":\[.+?\]")))['cmd_ids']
            for cms_id in cms_ids:
                yield scrapy.Request.from_curl(curl_request.format(cms_id), callback=self.parse_facebook_cms)
        except json.JSONDecodeError as err:
            logging.warning("Facebook cms retrieval failure: %s", err)
            raise err
        except KeyError:
            logging.warning("Facebook cms retrieval failure: No cmd_ids")
            raise err

    def parse_facebook_cms(self, response):
        pass
