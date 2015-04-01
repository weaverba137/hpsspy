# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def get_tmpdir(**kwargs):
    """Return the path to a suitable temporary directory.

    Resolves the path to the temporary directory in the following order:

    1. If ``tmpdir`` is present as a keyword argument, the value is returned.
    2. If :envvar:`TMPDIR` is set, its value is returned.
    3. If neither are set, ``/tmp`` is returned.

    Parameters
    ----------
    kwargs : dict
        Keyword arguments from another function may be passed to this
        function.  If ``tmpdir`` is present as a key, its value will be returned.

    Returns
    -------
    get_tmpdir : str
        The name of a temporary directory.
    """
    from os import environ
    if 'tmpdir' in kwargs:
        t = kwargs['tmpdir']
    elif 'TMPDIR' in environ:
        t = environ['TMPDIR']
    else:
        t = '/tmp'
    return t
