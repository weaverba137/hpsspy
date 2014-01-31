# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def hsi(*args):
    """Run hsi command with arguments."""
    from . import get_hpss_dir
    from os import remove
    from os.path import exists, join
    from subprocess import call
    try:
        path = get_hpss_dir()
    except:
        raise
    ofile = '/tmp/hsi.txt'
    base_command = [join(path,'hsi'),'-O', ofile, '-s', 'archive']
    command = base_command + list(args)
    status = call(command)
    with open(ofile) as o:
        out=o.read()
    if exists(ofile):
        remove(ofile)
    return out
