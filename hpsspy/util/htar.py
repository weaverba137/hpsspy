# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def htar(*args):
    """Run htar command with arguments.

    Parameters
    ----------
    args : tuple
        Arguments to be passed to the hsi command.

    Returns
    -------
    htar : tuple of str
        The standard output and standard error from the htar command.

    Raises
    ------
    ValueError
        If the ``$HPSS_DIR`` environment variable has not been set.
    """
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
