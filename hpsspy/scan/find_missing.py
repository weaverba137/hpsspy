# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
def find_missing(hpss_map,hpss_files,disk_files_cache,report=10000):
    """Compare HPSS files to disk files.

    Parameters
    ----------
    hpss_map : dict
        A mapping of file names to HPSS files.
    hpss_files : frozenset
        The list of actual HPSS files.
    disk_files_cache : str
        Name of the disk cache file.
    report : int, optional
        Print an informational message when N files have been scanned.

    Returns
    -------
    find_missing : int
        The number of missing files.
    """
    import logging
    from os.path import basename, dirname
    logger = logging.getLogger(__name__)
    nfiles = 0
    nmissing = 0
    with open(disk_files_cache) as t:
        for l in t:
            f = l.strip()
            message = "{0} NOT FOUND!".format(f)
            if f in hpss_map["exclude"]:
                message = "{0} skipped.".format(f)
            else:
                section = f.split('/')[0]
                for r in hpss_map[section]:
                    m = r[0].match(f)
                    if m is not None:
                        reName = r[0].sub(r[1],f)
                        if reName in hpss_files:
                            message = "{0} in {1}.".format(f,reName)
                        else:
                            if reName.endswith('.tar'):
                                if reName.endswith('_files.tar'):
                                    htar_dir = '-L files'
                                    chdir = dirname(reName)
                                else:
                                    htar_dir = basename(reName).split('_')[-1].split('.')[0]
                                    chdir = dirname(reName)
                                    while r[0].match(chdir) is not None:
                                        chdir = dirname(chdir)
                                    message = "cd {0}; hsi mkdir -p {0}; htar -cvf {1} {2}".format(chdir, reName, htar_dir)
                            else:
                                message = "hsi put {0} : {1}".format(f,reName)
                        break
            if message.endswith('NOT FOUND!'):
                logger.warning(message)
                nmissing += 1
            else:
                logger.debug(message)
            nfiles += 1
            if (nfiles % report) == 0:
                logger.info("{0:9d} files scanned.".format(nfiles))
    return nmissing
