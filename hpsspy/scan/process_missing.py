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
    from os import chdir, remove
    from os.path import basename, dirname, join
    from ..util import get_tmpdir, hsi, htar
    logger = logging.getLogger(__name__)
    logger.debug("Processing missing files from {0}.".format(missing_cache))
    with open(missing_cache) as fp:
        missing = json.load(fp)
    created_directories = set()
    for h in missing:
        h_file = join(hpss_root,h)
        if h.endswith('.tar'):
            if h.endswith('_files.tar'):
                disk_chdir = dirname(h)
                Lfile = join(get_tmpdir(),basename(h.replace('.tar','.txt')))
                htar_dir = None
                with open(Lfile,'w') as fp:
                    fp.write('\n'.join([basename(f) for f in missing[h]])+'\n')
            else:
                disk_chdir = dirname(h)
                Lfile = None
                htar_dir = basename(h).split('_')[-1].split('.')[0]
            logger.debug("chdir('{0}')".format(join(disk_root,disk_chdir)))
            chdir(join(disk_root,disk_chdir))
            h_dir = join(hpss_root,disk_chdir)
            if h_dir not in created_directories:
                logger.debug("hsi('mkdir', '-p', '-m', '{0}', '{1}')".format(dirmode,h_dir))
                # out = hsi('mkdir', '-p', '-m', dirmode, h_dir)
                # logger.debug(out)
                created_directories.add(h_dir)
            if Lfile is None:
                logger.debug("htar('-cvf', '{0}', '-H', 'crc:verify=all', '{1}')".format(h_file, htar_dir))
                # out, err = htar('-cvf', h_file, '-H', 'crc:verify=all', htar_dir)
            else:
                logger.debug("htar('-cvf', '{0}', '-H', 'crc:verify=all', '-L', '{1}')".format(h_file, Lfile))
                # out, err = htar('-cvf', h_file, '-H', 'crc:verify=all', '-L', Lfile)
            # logger.debug(out)
            # if err:
            #     logger.warn(err)
            if Lfile is not None:
                logger.debug("remove('{0}')".format(Lfile))
                # remove(Lfile)
        else:
            if dirname(h_file) not in created_directories:
                logger.debug("hsi('mkdir', '-p', '-m', '{0}', '{1}')".format(dirmode,dirname(h_file)))
                # out = hsi('mkdir', '-p', '-m', dirmode, dirname(h_file))
                # logger.debug(out)
                created_directories.add(dirname(h_file))
            logger.debug("hsi('put', '{0}', ':', '{1}')".format(join(disk_root,missing[h][0]),h_file))
            # out = hsi('put', join(disk_root,missing[h][0]), ':', h_file)
            # logger.debug(out)
    return
