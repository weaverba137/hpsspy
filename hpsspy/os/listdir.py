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
    files = list()
    for f in lines[2:]:
        if len(f) == 0:
            continue
        m = linere.match(f)
        if m is None:
            raise HpssOSError("Could not match line!\n{0}".format(f))
        files.append(m.groups())
    return files
