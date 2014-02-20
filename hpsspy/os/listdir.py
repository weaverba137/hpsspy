# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def listdir(path):
    """List the contents of an HPSS directory.

    Parameters
    ----------
    path : str

    Returns
    -------
    listdir : list

    """
    from . import linere
    from .. import HpssOSError
    from ..util import hpss_file, hsi
    out = hsi('ls','-la',path)
    if out.startswith('**'):
        raise HpssOSError(out)
    lines = out.split('\n')
    lspath = path # sometimes you don't get the path echoed back.
    found_path = False
    files = list()
    for f in lines:
        if len(f) == 0:
            continue
        if f.endswith(':') and not found_path:
            lspath = f.strip(': ')
            found_path = True
            continue
        m = linere.match(f)
        if m is None:
            raise HpssOSError("Could not match line!\n{0}".format(f))
        g = m.groups()
        files.append(hpss_file(lspath,*g))
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
