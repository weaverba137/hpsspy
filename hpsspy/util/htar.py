# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def htar(*args):
    """Run :command:`htar` with arguments.

    Parameters
    ----------
    args : tuple
        Arguments to be passed to :command:`htar`.

    Returns
    -------
    htar : tuple of str
        The standard output and standard error from :command:`htar`.

    Raises
    ------
    KeyError
        If the :envvar:`HPSS_DIR` environment variable has not been set.
    """
    from . import get_hpss_dir
    from tempfile import TemporaryFile
    from subprocess import call
    from os.path import join
    outfile=TemporaryFile()
    errfile=TemporaryFile()
    path = get_hpss_dir()
    command=[join(path,'htar')] + list(args)
    status=call(command,stdout=outfile,stderr=errfile)
    outfile.seek(0)
    out = outfile.read()
    errfile.seek(0)
    err = errfile.read()
    outfile.close()
    errfile.close()
    return (out,err)
