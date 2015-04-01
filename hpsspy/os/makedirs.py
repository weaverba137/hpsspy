# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def makedirs(path,mode=None):
    """Reproduces the behavior of os.makedirs().

    Parameters
    ----------
    path : str
        Directory to create.
    mode : str
        String representation of the octal directory mode.

    Returns
    -------
    None

    Notes
    -----
    Unlike ``os.makedirs()``, attempts to create existing directories raise no
    exception.
    """
    from .. import HpssOSError
    from ..util import hsi
    if mode is None:
        out = hsi('mkdir','-p',path)
    else:
        out = hsi('mkdir','-p','-m',mode,path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return
