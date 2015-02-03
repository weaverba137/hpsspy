# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def files_to_hpss(hpss_map_cache='sdss.json'):
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
    from pkg_resources import resource_exists, resource_stream
    from . import compile_map
    logger = logging.getLogger(__name__)
    if exists(hpss_map_cache):
        logger.info("Found map file {0}.".format(hpss_map_cache))
        with open(hpss_map_cache) as t:
            hpss_map = json.load(t)
    else:
        if resource_exists('hpsspy.data',hpss_map_cache):
            logger.info("Reading from file {0} in the hpsspy distribution.".format(hpss_map_cache))
            t = resource_stream('hpsspy.data',hpss_map_cache)
            hpss_map = json.load(t)
            t.close()
        else:
            logger.info("Returning empty map file!")
            hpss_map = {
                "dr8":{"exclude":[],"casload":{},"apogee":{},"boss":{},"sdss":{}},
                "dr9":{"exclude":[],"casload":{},"apogee":{},"boss":{},"sdss":{}},
                "dr10":{"exclude":[],"casload":{},"apogee":{},"boss":{},"sdss":{}},
                "dr11":{"exclude":[],"casload":{},"apogee":{},"boss":{},"marvels":{},"sdss":{}},
                "dr12":{"exclude":[],"casload":{},"apo":{},"apogee":{},"boss":{},"marvels":{},"sdss":{}},
                }
    return compile_map(hpss_map,options.release)
