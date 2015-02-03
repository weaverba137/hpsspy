# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def files_to_hpss(hpss_map_cache):
    """Create a map of files on disk to HPSS files.

    Parameters
    ----------
    hpss_map_cache : str
        Data file containing the map.

    Returns
    -------
    files_to_hpss : dict
        The mapping.
    """
    import logging
    import json
    from os.path import exists
    from . import compile_map
    logger = logging.getLogger(__name__)
    if exists(hpss_map_cache):
        logger.info("Found map file {0}.".format(hpss_map_cache))
        with open(hpss_map_cache) as t:
            hpss_map = json.load(t)
    else:
        hpss_map = {
            "dr8":{"exclude":[],"casload":{},"apogee":{},"boss":{},"sdss":{}},
            "dr9":{"exclude":[],"casload":{},"apogee":{},"boss":{},"sdss":{}},
            "dr10":{"exclude":[],"casload":{},"apogee":{},"boss":{},"sdss":{}},
            "dr11":{"exclude":[],"casload":{},"apogee":{},"boss":{},"marvels":{},"sdss":{}},
            "dr12":{"exclude":[],"casload":{},"apo":{},"apogee":{},"boss":{},"marvels":{},"sdss":{}},
            }
    hpss_map = compile_map(hpss_map,options.release)
