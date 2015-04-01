# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def islink(path):
    """Reproduces the behavior of os.islink() for HPSS files.
    """
    from .. import lstat
    return lstat(path).islink
