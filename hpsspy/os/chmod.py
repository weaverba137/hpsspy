# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def chmod(path,mode):
    """Reproduces the behavior of :func:`os.chmod` for HPSS files.

    Parameters
    ----------
    path : str
        File to chmod.
    mode : str or int
        Desired file permissions.  This mode will be converted to a string.
    """
    from .. import HpssOSError
    from ..util import hsi
    out = hsi('chmod',str(mode),path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return
