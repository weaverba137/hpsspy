# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def hsi(*args,**kwargs):
    """Run hsi command with arguments.

    Parameters
    ----------
    args : tuple
        Arguments to be passed to the hsi command.
    tmpdir : str, optional
        Write temporary files to this directory.  Defaults to '/tmp'.
        This option must be passed as a keyword!

    Returns
    -------
    hsi : str
        The standard output from the hsi command.

    Raises
    ------
    ValueError
        If the ``$HPSS_DIR`` environment variable has not been set.
    """
    from . import get_hpss_dir
    from os import environ, remove
    from os.path import exists, join
    from subprocess import call
    try:
        path = get_hpss_dir()
    except:
        raise
    if 'tmpdir' in kwargs:
        t = kwargs['tmpdir']
    elif 'TMPDIR' in environ:
        t = environ['TMPDIR']
    else:
        t = '/tmp'
    ofile = join(t,'hsi.txt')
    base_command = [join(path,'hsi'),'-O', ofile, '-s', 'archive']
    command = base_command + list(args)
    status = call(command)
    with open(ofile) as o:
        out=o.read()
    if exists(ofile):
        remove(ofile)
    return out
