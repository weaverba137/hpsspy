# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def htar(*args):
    """Run htar command with arguments."""
    from . import get_hpss_dir
    from tempfile import TemporaryFile
    from subprocess import call
    from os.path import join
    outfile=TemporaryFile()
    errfile=TemporaryFile()
    try:
        path = get_hpss_dir()
    except:
        raise
    command=[join(path,'htar')] + list(args)
    status=call(command,stdout=outfile,stderr=errfile)
    outfile.seek(0)
    out = outfile.read()
    errfile.seek(0)
    err = errfile.read()
    outfile.close()
    errfile.close()
    return (out,err)
