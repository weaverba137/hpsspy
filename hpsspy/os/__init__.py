# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.os
~~~~~~~~~

Reproduces some features of the Python built-in :mod:`os`.
"""
from ._os import *

import re

linere = re.compile(r"""([dl-])           # file type
                        ([rwxsStT-]+)\s+  # file permissions
                        (\d+)\s+          # number of links
                        (\S+)\s+          # user
                        (\S+)\s+          # group
                        (\d+)\s+          # size
                        ([A-Za-z]+)\s+    # month
                        (\d+)\s+          # day
                        ([0-9:]+)\s       # year
                        (.*)$             # filename
                        """, re.VERBOSE)

del re
