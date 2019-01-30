# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.os.path
~~~~~~~~~~~~~~

Reproduces some features of the Python built-in :mod:`os.path`.
"""


def isdir(path):
    """Reproduces the behavior of :func:`os.path.isdir` for HPSS files.

    Parameters
    ----------
    path : :class:`str`
        Path to the file.

    Returns
    -------
    :class:`bool`
        ``True`` if `path` is a directory.
    """
    from ._os import stat
    return stat(path).isdir


def isfile(path):
    """Reproduces the behavior of :func:`os.path.isfile` for HPSS files.

    Parameters
    ----------
    path : :class:`str`
        Path to the file.

    Returns
    -------
    :class:`bool`
        ``True`` if `path` is a file.
    """
    from ._os import stat
    return not stat(path).isdir


def islink(path):
    """Reproduces the behavior of :func:`os.path.islink` for HPSS files.

    Parameters
    ----------
    path : :class:`str`
        Path to the file.

    Returns
    -------
    :class:`bool`
        ``True`` if `path` is a symlink.
    """
    from ._os import lstat
    return lstat(path).islink
