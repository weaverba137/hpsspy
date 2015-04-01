# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def islink(path):
    """Reproduces the behavior of :func:`os.path.islink` for HPSS files.

    Parameters
    ----------
    path : str
        Path to the file.

    Returns
    -------
    islink : bool
        True if the path is a symlink.
    """
    from .. import lstat
    return lstat(path).islink
