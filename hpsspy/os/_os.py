# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.os._os
~~~~~~~~~~~~~

Contains the actual functions in :mod:`hpsspy.os`.
"""
from os.path import join
from .path import islink
from .. import HpssOSError
from ..util import HpssFile, hsi
import re

__all__ = ['chmod', 'listdir', 'makedirs', 'mkdir', 'stat', 'lstat', 'walk']

linere = re.compile(r"""([dl-])           # file type
                        ([rwxsStT-]+)\s+  # file permissions
                        (\d+)\s+          # number of links
                        (\S+)\s+          # user
                        (\S+)\s+          # group
                        (\d+)\s+          # size
                        ([A-Za-z]+)\s+    # day of week
                        ([A-Za-z]+)\s+    # month
                        (\d+)\s+          # day
                        ([0-9:]+)\s       # H:M:S
                        ([0-9]+)\s        # year
                        (.*)$             # filename
                        """, re.VERBOSE)


def chmod(path, mode):
    """Reproduces the behavior of :func:`os.chmod` for HPSS files.

    Parameters
    ----------
    path : :class:`str`
        File to chmod.
    mode : :class:`str` or :class:`int`
        Desired file permissions.  This mode will be converted to a string.

    Raises
    ------
    :class:`~hpsspy.HpssOSError`
        If the underlying :command:`hsi` reports an error.
    """
    out = hsi('chmod', str(mode), path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return


def _ls(path, options=''):
    """Perform :command:`hsi ls` and parse the results.

    Parameters
    ----------
    path : :class:`str`
        Directory or file to examine.
    options : :class:`str`, optional
        Options to ``ls`` that will be appended to a base set of options.
        The base set is ``-D``, which is needed for high-precision
        timestamps.

    Returns
    -------
    :class:`list`
        A list of :class:`~hpsspy.util.HpssFile` objects.
    """
    out = hsi('ls', '-D' + options, path)
    if out.startswith('**'):
        raise HpssOSError(out)
    lines = out.split('\n')
    lspath = path  # sometimes you don't get the path echoed back.
    files = list()
    for f in lines:
        if len(f) == 0:
            continue
        m = linere.match(f)
        if m is None:
            if f.endswith(':'):
                lspath = f.strip(': ')
            else:
                raise HpssOSError("Could not match line!\n{0}".format(f))
        else:
            g = m.groups()
            files.append(HpssFile(lspath, *g))
    return files


def listdir(path):
    """List the contents of an HPSS directory, similar to :func:`os.listdir`.

    Parameters
    ----------
    path : :class:`str`
        Directory to examine.

    Returns
    -------
    :class:`list`
        A list of :class:`~hpsspy.util.HpssFile` objects.

    Raises
    ------
    :class:`~hpsspy.HpssOSError`
        If the underlying :command:`hsi` reports an error.
    """
    files = _ls(path, options='a')
    #
    # Create a unique set of filenames for use below.
    #
    fileset = set([f.name for f in files])
    #
    # Go back and identify htar files
    #
    for f in files:
        if f.name.endswith('.tar') and f.name + '.idx' in fileset:
            f.ishtar = True
    return files


def makedirs(path, mode=None):
    """Reproduces the behavior of :func:`os.makedirs`.

    Parameters
    ----------
    path : :class:`str`
        Directory to create.
    mode : :class:`str`, optional
        String representation of the octal directory mode.

    Raises
    ------
    :class:`~hpsspy.HpssOSError`
        If the underlying :command:`hsi` reports an error.

    Notes
    -----
    Unlike :func:`os.makedirs`, attempts to create existing directories raise
    no exception.
    """
    if mode is None:
        out = hsi('mkdir', '-p', path)
    else:
        out = hsi('mkdir', '-p', '-m', mode, path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return


def mkdir(path, mode=None):
    """Reproduces the behavior of :func:`os.mkdir`.

    Parameters
    ----------
    path : :class:`str`
        Directory to create.
    mode : :class:`str`, optional
        String representation of the octal directory mode.

    Raises
    ------
    :class:`~hpsspy.HpssOSError`
        If the underlying :command:`hsi` reports an error.

    Notes
    -----
    Unlike :func:`os.mkdir`, attempts to create existing directories raise no
    exception.
    """
    if mode is None:
        out = hsi('mkdir', path)
    else:
        out = hsi('mkdir', '-m', mode, path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return


def stat(path, follow_symlinks=True):
    """Perform the equivalent of :func:`os.stat` on the HPSS file `path`.

    Parameters
    ----------
    path : :class:`str`
        Path to file or directory.
    follow_symlinks : :class:`bool`, optional
        If ``False``, makes :func:`stat` behave like :func:`os.lstat`.

    Returns
    -------
    :class:`~hpsspy.util.HpssFile`
        An object that contains information similar to the data returned by
        :func:`os.stat`.

    Raises
    ------
    :class:`~hpsspy.HpssOSError`
        If the underlying :command:`hsi ls` reports an error.
    """
    files = _ls(path, options='d')
    if len(files) != 1:
        raise HpssOSError("Non-unique response for {0}!".format(path))
    if files[0].islink and follow_symlinks:
        return stat(files[0].readlink)
    else:
        return files[0]


def lstat(path):
    """Perform the equivalent of :func:`os.lstat` on the HPSS file `path`.

    Parameters
    ----------
    path : :class:`str`
        Path to file or directory.

    Returns
    -------
    :class:`~hpsspy.util.HpssFile`
        An object that contains information similar to the data returned by
        :func:`os.stat`.

    Raises
    ------
    :class:`~hpsspy.HpssOSError`
        If the underlying :command:`hsi` reports an error.
    """
    return stat(path, follow_symlinks=False)


def walk(top, topdown=True, onerror=None, followlinks=False):
    """Traverse a directory tree on HPSS, similar to :func:`os.walk`.

    Parameters
    ----------
    top : :class:`str`
        Starting directory.
    topdown : :class:`bool`, optional
        Direction to traverse the directory tree.
    onerror : callable, optional
        Call this function if an error is detected.
    followlinks : :class:`bool`, optional
        If ``True`` symlinks to directories are treated as directories.

    Returns
    -------
    iterable
        This function can be used in the same way as :func:`os.walk`.
    """
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
