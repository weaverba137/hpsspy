# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def walk(top,topdown=True,onerror=None,followlinks=False):
    """Traverse a directory tree on HPSS, similar to :func:`os.walk`.

    Parameters
    ----------
    top : str
        Starting directory.
    topdown : bool, optional
        Direction to traverse the directory tree.
    onerror : callable, optional
        Call this function if an error is detected.
    followlinks : bool, optional
        If ``True`` symlinks to directories are treated as directories.

    Returns
    -------
    walk : iterable
        This function can be used in the same way as :func:`os.walk`.
    """
    from .. import HpssOSError
    from . import listdir
    from .path import islink
    from os.path import join
    #
    # We may not have read permission for top, in which case we can't
    # get a list of the files the directory contains.  os.path.walk
    # always suppressed the exception then, rather than blow up for a
    # minor reason when (say) a thousand readable directories are still
    # left to visit.  That logic is copied here.
    #
    try:
        names = listdir(top)
    except HpssOSError as err:
        if onerror is not None:
            onerror(err)
        return
    dirs, nondirs = [], []
    for name in names:
        if name.isdir:
            dirs.append(name)
        else:
            nondirs.append(name)
    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = join(top, str(name))
        if followlinks or not islink(new_path):
            for x in walk(new_path, topdown, onerror, followlinks):
                yield x
    if not topdown:
        yield top, dirs, nondirs
