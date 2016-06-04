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
from re import compile
#
linere = compile('([dl-])([rwxsStT-]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+([A-Za-z]+)\s+(\d+)\s+([0-9:]+) (.*)$')
htarre = compile('HTAR: ([dl-])([rwxsStT-]+)\s+([^/]+)/(\S+)\s+(\d+)\s+(\d+)-(\d+)-(\d+)\s+([0-9:]+)\s+(\S.*)$')
from . import path
from .chmod import chmod
from .listdir import listdir
from .makedirs import makedirs
from .mkdir import mkdir
from .stat import lstat, stat
from .walk import walk

del compile
