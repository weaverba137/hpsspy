# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def chmod(path,mode):
    """
    """
    from .. import HpssOSError
    from ..util import hsi
    out = hsi('chmod',mode,path)
    if out.startswith('**'):
        raise HpssOSError(out)
    return
