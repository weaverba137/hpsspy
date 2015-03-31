# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def process_missing(missing_cache,disk_root,hpss_root,dirmode='2770'):
    """Convert missing files into HPSS commands.

    Parameters
    ----------
    missing_cache : str
        Name of a JSON file containing the missing file data.
    disk_root : str
        Missing files are relative to this root on disk.
    hpss_root : str
        Missing files are relative to this root on HPSS.
    dirmode : str
        Create directories on HPSS with this mode.

    Returns
    -------
    None
    """
    import logging
    import json
    from os import chdir
    from os.path import basename, dirname, join
    from ..util import hsi, htar
    logger = logging.getLogger(__name__)
    logger.debug("Processing missing files from {0}.".format(missing_cache))
    with open(missing_cache) as fp:
        missing = json.load(fp)
    created_directories = set()
    for h in missing:
        if h.endswith('.tar'):
            if h.endswith('_files.tar'):
                htar_dir = '-L files'
                disk_chdir = dirname(h)
            else:
                htar_dir = basename(h).split('_')[-1].split('.')[0]
                disk_chdir = dirname(h)
            logger.debug("chdir('{0}')".format(join(disk_root,disk_chdir)))
            # chdir(join(disk_root,disk_chdir))
            h_dir = join(hpss_root,disk_chdir)
            if h_dir not in created_directories:
                logger.debug("hsi('mkdir', '-p', '-m', '{0}', '{1}')".format(dirmode,h_dir))
                # out = hsi('mkdir', '-p', '-m', dirmode, h_dir)
                created_directories.add(h_dir)
            logger.debug("htar('-cvf', '{0}', '-H', 'crc:verify=all', '{1}')".format(hpss_root,h), htar_dir)
        else:
            logger.debug("hsi('put', '{0}', ':', '{1}')".format(join(disk_root,missing[h][0]),join(hpss_root,h)))
    return
