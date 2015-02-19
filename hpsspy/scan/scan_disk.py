# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def scan_disk(disk_roots,disk_files_cache):
    """Scan a directory tree on disk and cache the files found there.

    Parameters
    ----------
    disk_roots : list
        Name(s) of a directory in which to start the scan.
    disk_files_cache : str
        Name of a file to hold the cache.

    Returns
    -------
    scan_hpss : bool
        Returns ``True`` if the cache is populated and ready to read.
    """
    import logging
    import os
    from os.path import exists, islink
    logger = logging.getLogger(__name__)
    if exists(disk_files_cache):
        logger.debug("Using existing file cache: {0}".format(disk_files_cache))
        return True
    else:
        logger.info("No disk cache file, starting scan.")
        with open(disk_files_cache,'w') as t:
            try:
                for disk_root in disk_roots:
                    disk_files = list()
                    for root, dirs, files in os.walk(disk_root):
                        logger.debug("Scanning disk directory {0}.".format(root))
                        disk_files += [join(root,f).replace(disk_root+'/','') for f in files if not islink(join(root,f))]
                    t.write('\n'.join(disk_files)+'\n')
            except:
                logger.error('Exception encountered while creating disk cache file!')
                return False
    return True
