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
    """Generic exception class for HPSS Errors.
    """
    pass

class HpssOSError(HpssError):
    """HPSS Errors that are similar to OSError.
    """
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
__version__ = '0.1.0.dev'
