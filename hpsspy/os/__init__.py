# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.os
~~~~~~~~~

Reproduces some features of the Python built-in :mod:`os`.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
from . import path
from ._os import *
from re import compile


linere = compile('([dl-])([rwxsStT-]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+([A-Za-z]+)\s+(\d+)\s+([0-9:]+) (.*)$')

del compile
