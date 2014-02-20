# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def isdir(path):
    """
    """
    from .. import stat
    return stat(path).isdir
