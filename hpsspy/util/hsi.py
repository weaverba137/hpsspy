# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def hsi(*args,**kwargs):
    """Run :command:`hsi` with arguments.

    Parameters
    ----------
    args : tuple
        Arguments to be passed to :command:`hsi`.
    tmpdir : str, optional
        Write temporary files to this directory.  Defaults to the value
        returned by :func:`hpsspy.util.get_tmpdir`. This option must be
        passed as a keyword!

    Returns
    -------
    hsi : str
        The standard output from :command:`hsi`.

    Raises
    ------
    KeyError
        If the :envvar:`HPSS_DIR` environment variable has not been set.
    """
    from . import get_hpss_dir, get_tmpdir
    from os import remove
    from os.path import exists, join
    from subprocess import call
    path = get_hpss_dir()
    ofile = join(get_tmpdir(**kwargs),'hsi.txt')
    base_command = [join(path,'hsi'),'-O', ofile, '-s', 'archive']
    command = base_command + list(args)
    status = call(command)
    with open(ofile) as o:
        out=o.read()
    if exists(ofile):
        remove(ofile)
    return out
