# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def mkdir(path,mode=None):
    """
    Notes
    -----
    Unlike ``os.mkdir()``, attempts to create existing directories raise no
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
