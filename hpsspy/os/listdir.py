# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def listdir(path):
    """
    """
    from . import linere
    from .. import HpssOSError
    from ..util import hsi
    import re
    out = hsi('ls','-la',path)
    if out.startswith('**'):
        raise HpssOSError(out)
    lines = out.split('\n')
    lspath = lines[1]
    for f in lines[2:]:
        m = linere.match(f)
        if m is None:
            raise HpssOSError("Could not match line!\n{0}".format(f))
        g = m.groups()
    return g
