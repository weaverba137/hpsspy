# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.scan
~~~~~~~~~~~

Functions for scanning directory trees to find files in need of backup.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def compile_map(old_map, release):
    """Compile the regular expressions in a map.

    Parameters
    ----------
    old_map : :class:`dict`
        A dictionary containing regular expressions to compile.
    release : :class:`str`
        An initial key to determine the section of the dictionary of interest.

    Returns
    -------
    :class:`dict`
        A new dictionary containing compiled regular expressions.
    """
    from re import compile
    new_map = dict()
    for key in old_map[release]:
        if key == 'exclude':
            new_map[key] = frozenset(old_map[release][key])
        else:
            foo = list()
            for r in old_map[release][key]:
                foo.append((compile(r), old_map[release][key][r]))
            new_map[key] = tuple(foo)
    return new_map


def files_to_hpss(hpss_map_cache, release):
    """Create a map of files on disk to HPSS files.

    Parameters
    ----------
    hpss_map_cache : :class:`str`
        Data file containing the map.
    release : :class:`str`
        Release name.

    Returns
    -------
    :func:`tuple`
        A tuple contiaining the compiled mapping and an additional
        configuration dictionary.
    """
    import logging
    import json
    from os.path import exists
    from pkg_resources import resource_exists, resource_stream
    logger = logging.getLogger(__name__ + '.files_to_hpss')
    if exists(hpss_map_cache):
        logger.info("Found map file {0}.".format(hpss_map_cache))
        with open(hpss_map_cache) as t:
            hpss_map = json.load(t)
    else:
        if resource_exists('hpsspy.data', hpss_map_cache):
            logger.info(("Reading from file {0} in the hpsspy " +
                         "distribution.").format(hpss_map_cache))
            t = resource_stream('hpsspy.data', hpss_map_cache)
            hpss_map = json.load(t)
            t.close()
        else:
            logger.warning("Returning empty map file!")
            hpss_map = {"config": {},
                        "dr8": {"exclude": [], "casload": {}, "apogee": {},
                                "boss": {}, "sdss": {}},
                        "dr9": {"exclude": [], "casload": {}, "apogee": {},
                                "boss": {}, "sdss": {}},
                        "dr10": {"exclude": [], "casload": {}, "apogee": {},
                                 "boss": {}, "sdss": {}},
                        "dr11": {"exclude": [], "casload": {}, "apogee": {},
                                 "boss": {}, "marvels": {}, "sdss": {}},
                        "dr12": {"exclude": [], "casload": {}, "apo": {},
                                 "apogee": {}, "boss": {}, "marvels": {},
                                 "sdss": {}}}
    return (compile_map(hpss_map, release), hpss_map['config'])


def find_missing(hpss_map, hpss_files, disk_files_cache, missing_files,
                 report=10000):
    """Compare HPSS files to disk files.

    Parameters
    ----------
    hpss_map : :class:`dict`
        A mapping of file names to HPSS files.
    hpss_files : :class:`frozenset`
        The list of actual HPSS files.
    disk_files_cache : :class:`str`
        Name of the disk cache file.
    missing_files : :class:`str`
        Name of the file that will contain the list of missing files.
    report : :class:`int`, optional
        Print an informational message when N files have been scanned.

    Returns
    -------
    :class:`int`
        The number of missing files.
    """
    import logging
    import json
    from os.path import basename, dirname
    logger = logging.getLogger(__name__ + '.find_missing')
    nfiles = 0
    nmissing = 0
    missing = dict()
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
                        reName = r[0].sub(r[1], f)
                        if reName in hpss_files:
                            message = "{0} in {1}.".format(f, reName)
                        else:
                            if reName in missing:
                                missing[reName].append(f)
                            else:
                                missing[reName] = [f]
                        break
            if message.endswith('NOT FOUND!'):
                logger.warning(message)
                nmissing += 1
            else:
                logger.debug(message)
            nfiles += 1
            if (nfiles % report) == 0:
                logger.info("{0:9d} files scanned.".format(nfiles))
    with open(missing_files, 'w') as fp:
        json.dump(missing, fp, indent=2, separators=(',', ': '))
    return nmissing


def process_missing(missing_cache, disk_root, hpss_root, dirmode='2770'):
    """Convert missing files into HPSS commands.

    Parameters
    ----------
    missing_cache : :class:`str`
        Name of a JSON file containing the missing file data.
    disk_root : :class:`str`
        Missing files are relative to this root on disk.
    hpss_root : :class:`str`
        Missing files are relative to this root on HPSS.
    dirmode : :class:`str`
        Create directories on HPSS with this mode.
    """
    import logging
    import json
    from os import chdir, remove
    from os.path import basename, dirname, join
    from .os import makedirs
    from .util import get_tmpdir, hsi, htar
    logger = logging.getLogger(__name__ + '.process_missing')
    logger.debug("Processing missing files from {0}.".format(missing_cache))
    with open(missing_cache) as fp:
        missing = json.load(fp)
    created_directories = set()
    for h in missing:
        h_file = join(hpss_root, h)
        if h.endswith('.tar'):
            if h.endswith('_files.tar'):
                disk_chdir = dirname(h)
                Lfile = join(get_tmpdir(), basename(h.replace('.tar', '.txt')))
                htar_dir = None
                with open(Lfile, 'w') as fp:
                    fp.write('\n'.join([basename(f) for f in missing[h]])+'\n')
            else:
                disk_chdir = dirname(h)
                Lfile = None
                htar_dir = basename(h).split('_')[-1].split('.')[0]
            logger.debug("chdir('{0}')".format(join(disk_root, disk_chdir)))
            chdir(join(disk_root, disk_chdir))
            h_dir = join(hpss_root, disk_chdir)
            if h_dir not in created_directories:
                logger.debug(("makedirs('{0}', " +
                              "mode='{1}')").format(h_dir, dirmode))
                makedirs(h_dir, mode=dirmode)
                created_directories.add(h_dir)
            if Lfile is None:
                logger.debug(("htar('-cvf', '{0}', '-H', " +
                              "'crc:verify=all', '{1}')").format(h_file,
                                                                 htar_dir))
                out, err = htar('-cvf', h_file, '-H', 'crc:verify=all',
                                htar_dir)
            else:
                logger.debug(("htar('-cvf', '{0}', '-H', 'crc:verify=all', " +
                              "'-L', '{1}')").format(h_file, Lfile))
                out, err = htar('-cvf', h_file, '-H', 'crc:verify=all', '-L',
                                Lfile)
            logger.debug(out)
            if err:
                logger.warn(err)
            if Lfile is not None:
                logger.debug("remove('{0}')".format(Lfile))
                remove(Lfile)
        else:
            if dirname(h_file) not in created_directories:
                logger.debug(("makedirs('{0}', " +
                              "mode='{1}')").format(dirname(h_file), dirmode))
                makedirs(dirname(h_file), mode=dirmode)
                created_directories.add(dirname(h_file))
            logger.debug(("hsi('put', '{0}', ':', " +
                          "'{1}')").format(join(disk_root, missing[h][0]),
                                           h_file))
            out = hsi('put', join(disk_root, missing[h][0]), ':', h_file)
            logger.debug(out)
    return


def scan_disk(disk_roots, disk_files_cache, clobber=False):
    """Scan a directory tree on disk and cache the files found there.

    Parameters
    ----------
    disk_roots : :class:`list`
        Name(s) of a directory in which to start the scan.
    disk_files_cache : :class:`str`
        Name of a file to hold the cache.
    clobber : :class:`bool`, optional
        If ``True``, ignore any existing cache files.

    Returns
    -------
    :class:`bool`
        Returns ``True`` if the cache is populated and ready to read.
    """
    import logging
    import os
    from os.path import exists, islink, join
    logger = logging.getLogger(__name__ + '.scan_disk')
    if exists(disk_files_cache) and not clobber:
        logger.debug("Using existing file cache: {0}".format(disk_files_cache))
        return True
    else:
        logger.info("No disk cache file, starting scan.")
        with open(disk_files_cache, 'w') as t:
            try:
                for disk_root in disk_roots:
                    logger.debug("Starting os.walk at {0}.".format(disk_root))
                    for root, dirs, files in os.walk(disk_root):
                        logger.debug(("Scanning disk directory " +
                                      "{0}.").format(root))
                        disk_files = [join(root, f).replace(disk_root+'/',
                                                            '')+'\n'
                                      for f in files
                                      if not islink(join(root, f))]
                        t.writelines(disk_files)
            except:
                logger.error(('Exception encountered while creating ' +
                              'disk cache file!'))
                return False
    return True


def scan_hpss(hpss_root, hpss_files_cache, clobber=False):
    """Scan a directory on HPSS and return the files found there.

    Parameters
    ----------
    hpss_root : :class:`str`
        Name of a directory in which to start the scan.
    hpss_files_cache : :class:`str`
        Name of a file to hold the cache.
    clobber : :class:`bool`, optional
        If ``True``, ignore any existing cache files.

    Returns
    -------
    :class:`frozenset`
        The set of files found on HPSS.
    """
    import logging
    from os.path import exists
    from .os import walk
    logger = logging.getLogger(__name__ + '.scan_hpss')
    if exists(hpss_files_cache) and not clobber:
        logger.info("Found cache file {0}.".format(hpss_files_cache))
        with open(hpss_files_cache) as t:
            hpss_files = [l.strip() for l in t.readlines()]
    else:
        logger.info(("No HPSS cache file, starting scan " +
                     "at {0}.").format(hpss_root))
        hpss_files = list()
        for root, dirs, files in walk(hpss_root):
            # hpss_files += [f.path.replace(hpss_root+'/','')
            #                for f in files if not f.ishtar]
            logger.debug("Scanning HPSS directory {0}.".format(root))
            hpss_files += [f.path.replace(hpss_root+'/', '')
                           for f in files if not f.path.endswith('.idx')]
            # htar_files = [f for f in files if f.ishtar]
            # for h in htar_files:
            #     contents = h.htar_contents()
            #     hpss_files += [join(root,c[9]).replace(hpss_root+'/','')
            #                    for c in contents if c[0] == '-']
            # links += [f for f in files if f.islink]
        with open(hpss_files_cache, 'w') as t:
            t.write('\n'.join(hpss_files)+'\n')
    hpss_files = frozenset(hpss_files)
    return hpss_files


def main():
    """Entry-point for command-line scripts.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    import os
    import logging
    from argparse import ArgumentParser
    from sys import argv
    from os import getenv
    from os.path import basename, join
    #
    # Options
    #
    desc = 'Verify the presence of files on HPSS.'
    parser = ArgumentParser(prog=basename(argv[0]), description=desc)
    parser.add_argument('-c', '--clobber-disk', action='store_true',
                        dest='clobber_disk',
                        help='Ignore any existing disk cache files.')
    parser.add_argument('-C', '--clobber-hpss', action='store_true',
                        dest='clobber_hpss',
                        help='Ignore any existing HPSS cache files.')
    parser.add_argument('-p', '--process', action='store_true',
                        dest='process',
                        help=('Process the list of missing files to produce ' +
                              'HPSS commands.'))
    parser.add_argument('-r', '--report', action='store', type=int,
                        dest='report', metavar='N', default=10000,
                        help=("Print an informational message after " +
                              "every N files."))
    parser.add_argument('-v', '--verbose', action='store_true',
                        dest='verbose',
                        help="Increase verbosity.")
    parser.add_argument('config', metavar='FILE',
                        help="Read configuration from FILE.")
    parser.add_argument('release', metavar='SECTION',
                        help="Read SECTION from the configuration file.")
    options = parser.parse_args()
    #
    # Logging
    #
    ll = logging.INFO
    if options.verbose:
        ll = logging.DEBUG
    log_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    logging.basicConfig(level=ll, format=log_format,
                        datefmt='%Y-%m-%dT%H:%M:%S')
    logger = logging.getLogger(__name__)
    #
    # Config file
    #
    if options.config not in ('sdss', 'desi'):
        logger.error('Unsupported configuration: {0}'.format(options.config))
        return 1
    hpss_map, config = files_to_hpss(options.config+'.json', options.release)
    release_root = join(config['root'], options.release)
    hpss_release_root = join(config['hpss_root'], options.release)
    #
    # Read HPSS files and cache.
    #
    hpss_files_cache = join(getenv('HOME'), 'scratch',
                            'hpss_files_{0}.txt'.format(options.release))
    logger.debug('HPSS file cache = {0}'.format(hpss_files_cache))
    hpss_files = scan_hpss(hpss_release_root, hpss_files_cache,
                           clobber=options.clobber_hpss)
    #
    # Read disk files and cache.
    #
    disk_files_cache = join(getenv('HOME'), 'scratch',
                            'disk_files_{0}.txt'.format(options.release))
    logger.debug('Disk file cache = {0}'.format(disk_files_cache))
    disk_roots = [release_root.replace(basename(config['root']), d)
                  for d in config['physical_disks']]
    status = scan_disk(disk_roots, disk_files_cache,
                       clobber=options.clobber_disk)
    if not status:
        return 1
    #
    # See if the files are on HPSS.
    #
    missing_files_cache = join(getenv('HOME'), 'scratch',
                               ('missing_files_' +
                                '{0}.json').format(options.release))
    logger.debug('Missing files list = {0}'.format(missing_files_cache))
    missing = find_missing(hpss_map, hpss_files, disk_files_cache,
                           missing_files_cache, options.report)
    logger.debug("Found {0:d} missing files.".format(missing))
    #
    # Post process to generate HPSS commands
    #
    if missing > 0 and options.process:
        process_missing(missing_files_cache, release_root, hpss_release_root)
    return 0
