# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def mkdir(path,mode=None):
    """Reproduces the behavior of :func:`os.mkdir`.

    Parameters
    ----------
    path : str
        Directory to create.

    Returns
    -------
    None

    Notes
    -----
    Unlike :func:`os.mkdir`, attempts to create existing directories raise no
    exception.
    """
    from .. import HpssOSError
    from ..util import hsi
    if mode is None:
        out = hsi('mkdir',path)
    else:
        out = hsi('mkdir','-m',mode,path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return
