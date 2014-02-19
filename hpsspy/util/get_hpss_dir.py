# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
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
    ValueError
        If the ``$HPSS_DIR`` environment variable has not been set.
    """
    from os import getenv
    from os.path import join
    hpss_dir = getenv('HPSS_DIR')
    if hpss_dir is None:
        raise ValueError("HPSS_DIR is not set!")
    return join(hpss_dir,'bin')
