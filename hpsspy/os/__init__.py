# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
=========
hpsspy.os
=========

Reproduces some features of the Python built-in `os module`_.

.. _`os module`: http://docs.python.org/2/library/os.html
"""
from re import compile

linere = compile('([dl-])([rwxsStT-]+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\d+)\s+([A-Za-z]+)\s+(\d+)\s+([0-9:]+) (.*)$')

from . import path
from .chmod import chmod
from .listdir import listdir
from .mkdir import mkdir
from .stat import lstat, stat
from .walk import walk

del compile
