#!/usr/bin/env python3
# TODO

import logging as root_logger

import pyparsing as pp
from pyparsing import pyparsing_common as ppc

logging = root_logger.getLogger(__name__)

s = pp.Suppress
op = pp.Optional
opLn = s(op(pp.LineEnd()))
