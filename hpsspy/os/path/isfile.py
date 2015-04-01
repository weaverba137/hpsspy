# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def isfile(path):
    """Reproduces the behavior of :func:`os.path.isfile` for HPSS files.

    Parameters
    ----------
    path : str
        Path to the file.

    Returns
    -------
    isfile : bool
        True if the path is a file.
    """
    from .. import stat
    return not stat(path).isdir
