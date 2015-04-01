# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def isdir(path):
    """Reproduces the behavior of :func:`os.path.isdir` for HPSS files.

    Parameters
    ----------
    path : str
        Path to the file.

    Returns
    -------
    isdir : bool
        True if the path is a directory.
    """
    from .. import stat
    return stat(path).isdir
