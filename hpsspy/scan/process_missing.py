# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def process_missing(missing_cache,disk_root,hpss_root):
    """Convert missing files into HPSS commands.

    Parameters
    ----------
    missing_cache : str
        Name of a JSON file containing the missing file data.
    disk_root : str
        Missing files are relative to this root on disk.
    hpss_root : str
        Missing files are relative to this root on HPSS.

    Returns
    -------
    None
    """
    import logging
    import json
    from os.path import basename, dirname
    logger = logging.getLogger(__name__)
    logger.debug("Processing missing files from {0}.".format(missing_cache))
    with open(missing_cache) as fp:
        missing = json.load(fp)
    for h in missing:
        if h.endswith('.tar'):
            if h.endswith('_files.tar'):
                htar_dir = '-L files'
                chdir = dirname(h)
            else:
                htar_dir = basename(h).split('_')[-1].split('.')[0]
                chdir = dirname(h)
            command = "cd {0}; hsi mkdir -p {0}; htar -cvf {1} {2}".format(chdir, h, htar_dir)
        else:
            command = "hsi put {0} : {1}".format(missing[h][0],h)
        logger.debug(command)
    return
