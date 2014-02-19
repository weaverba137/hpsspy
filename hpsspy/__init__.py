# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
======
hpsspy
======

Python interface to the HPSS system.
"""
from . import os
from . import util

class HpssError(Exception):
    pass

class HpssOSError(HpssError):
    pass
