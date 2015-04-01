# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
def scan_disk(disk_roots,disk_files_cache,clobber=False):
    """Scan a directory tree on disk and cache the files found there.

    Parameters
    ----------
    disk_roots : list
        Name(s) of a directory in which to start the scan.
    disk_files_cache : str
        Name of a file to hold the cache.
    clobber : bool, optional
        If ``True``, ignore any existing cache files.

    Returns
    -------
    scan_hpss : bool
        Returns ``True`` if the cache is populated and ready to read.
    """
    import logging
    import os
    from os.path import exists, islink, join
    logger = logging.getLogger(__name__)
    if exists(disk_files_cache) and not clobber:
        logger.debug("Using existing file cache: {0}".format(disk_files_cache))
        return True
    else:
        logger.info("No disk cache file, starting scan.")
        with open(disk_files_cache,'w') as t:
            try:
                for disk_root in disk_roots:
                    logger.debug("Starting os.walk at {0}.".format(disk_root))
                    for root, dirs, files in os.walk(disk_root):
                        logger.debug("Scanning disk directory {0}.".format(root))
                        disk_files = [join(root,f).replace(disk_root+'/','')+'\n' for f in files if not islink(join(root,f))]
                        t.writelines(disk_files)
            except:
                logger.error('Exception encountered while creating disk cache file!')
                return False
    return True
