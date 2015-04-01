# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def stat(path,lstat=False):
    """Perform the equivalent of ``os.stat()`` on the HPSS file `path`.

    Parameters
    ----------
    path : str
    lstat : bool, optional
        If ``True``, makes `stat` behave like ``os.lstat()``.

    Returns
    -------
    stat : hpsspy.util.hpss_file
    """
    from . import linere
    from .. import HpssOSError
    from ..util import hpss_file, hsi
    from os.path import join
    out = hsi('ls','-ld',path)
    if out.startswith('**'):
        raise HpssOSError(out)
    lines = out.split('\n')
    lspath = path # sometimes you don't get the path echoed back.
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
            files.append(hpss_file(lspath,*g))
    if len(files) != 1:
        raise HpssOSError("Non-unique response for {0}!".format(path))
    if files[0].islink and not lstat:
        new_path = files[0].readlink
        if new_path.startswith('/'):
            return stat(new_path)
        else:
            return stat(join(lspath,new_path))
    else:
        return files[0]
#
#
#
def lstat(path):
    """Perform the equivalent of ``os.lstat()`` on the HPSS file `path`.
    """
    return stat(path,lstat=True)
