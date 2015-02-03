# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
======
hpsspy
======

Python interface to the HPSS system.
"""
#
# Exceptions
#
class HpssError(Exception):
    pass

class HpssOSError(HpssError):
    pass
#
# Set up namespace
#
from . import os
from . import scan
from . import util
#
#
#
__version__ = '0.1.0'
