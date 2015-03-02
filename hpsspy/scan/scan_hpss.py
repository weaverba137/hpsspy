# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def scan_hpss(hpss_root,hpss_files_cache,clobber=False):
    """Scan a directory on HPSS and return the files found there.

    Parameters
    ----------
    hpss_root : str
        Name of a directory in which to start the scan.
    hpss_files_cache : str
        Name of a file to hold the cache.
    clobber : bool, optional
        If ``True``, ignore any existing cache files.

    Returns
    -------
    scan_hpss : frozenset
        The set of files found on HPSS.
    """
    import logging
    from os.path import exists
    from ..os import walk
    logger = logging.getLogger(__name__)
    if exists(hpss_files_cache) and not clobber:
        logger.info("Found cache file {0}.".format(hpss_files_cache))
        with open(hpss_files_cache) as t:
            hpss_files = [l.strip() for l in t.readlines()]
    else:
        logger.info("No HPSS cache file, starting scan.")
        hpss_files = list()
        for root, dirs, files in walk(hpss_root):
            # hpss_files += [f.path.replace(hpss_root+'/','') for f in files if not f.ishtar]
            logger.debug("Scanning HPSS directory {0}.".format(root))
            hpss_files += [f.path.replace(hpss_root+'/','') for f in files if not f.path.endswith('.idx')]
            # htar_files = [f for f in files if f.ishtar]
            # for h in htar_files:
            #     contents = h.htar_contents()
            #     hpss_files += [join(root,c[9]).replace(hpss_root+'/','') for c in contents if c[0] == '-']
            # links += [f for f in files if f.islink]
        with open(hpss_files_cache,'w') as t:
            t.write('\n'.join(hpss_files)+'\n')
    hpss_files = frozenset(hpss_files)
    return hpss_files
