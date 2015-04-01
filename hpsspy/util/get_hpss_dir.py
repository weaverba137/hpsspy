# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def get_hpss_dir():
    """Return the directory containing HPSS commands.

    Parameters
    ----------
    None

    Returns
    -------
    get_hpss_dir : str
        Full path to the directory containing HPSS commands.

    Raises
    ------
    KeyError
        If the ``$HPSS_DIR`` environment variable has not been set.
    """
    from os import environ
    from os.path import join
    hpss_dir = environ['HPSS_DIR']
    return join(hpss_dir,'bin')
