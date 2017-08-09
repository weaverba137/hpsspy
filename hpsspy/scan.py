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


def validate_configuration(config):
    """Check the configuration file for validity.

    Parameters
    ----------
    config : :class:`str`
        Name of the configuration file.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    import logging
    import json
    from os.path import basename, splitext
    logger = logging.getLogger(__name__ + '.files_to_hpss')
    foo, xtn = splitext(basename(config))
    if xtn != '.json':
        logger.warning("%s might not be a JSON file!", config)
    try:
        with open(config) as fp:
            try:
                json_data = json.load(fp)
            except json.JSONDecodeError:
                logger.critical("%s is not valid JSON.", config)
                return 1
    except FileNotFoundError:
        logger.critical("%s does not exist. Try again.", config)
        return 1
    if 'config' in json_data:
        for k in ('root', 'hpss_root', 'physical_disks'):
            if k not in json_data['config']:
                logger.warning("%s 'config' section does not contain an " +
                               "entry for '%s'.", config, k)
    else:
        logger.critical("%s does not contain a 'config' section.", config)
        return 1
    for k in json_data:
        if k == 'config':
            continue
        if 'exclude' not in json_data[k]:
            logger.warning("Section '%s' should at least have an " +
                           "'exclude' entry.", k)
        try:
            new_map = compile_map(json_data, k)
        except re.error:
            logger.critical("Regular Expression error detected in " +
                            "section '%s'!", k)
            return 1
    return 0


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
        logger.info("Found map file %s.", hpss_map_cache)
        with open(hpss_map_cache) as t:
            hpss_map = json.load(t)
    else:
        if resource_exists('hpsspy.data', hpss_map_cache):
            logger.info("Reading from file %s in the hpsspy distribution.",
                        hpss_map_cache)
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
                 report=10000, limit=1024.0):
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
    limit : :class:`float`, optional
        HPSS archive files should be smaller than this size (in GB).

    Returns
    -------
    :class:`bool`
        ``True`` if no serious problems were found.
    """
    import logging
    import json
    import csv
    from os.path import basename, dirname
    logger = logging.getLogger(__name__ + '.find_missing')
    nfiles = 0
    nmissing = 0
    nmultiple = 0
    missing = dict()
    pattern_used = dict()
    section_warning = set()
    with open(disk_files_cache) as t:
        reader = csv.DictReader(t)
        for row in reader:
            f = row['Name']
            nfiles += 1
            if f in hpss_map["exclude"]:
                logger.info("%s is excluded.", f)
                continue
            section = f.split('/')[0]
            try:
                s = hpss_map[section]
            except KeyError:
                #
                # If the section is not described, that's not
                # good, but continue.
                #
                if section not in section_warning:
                    section_warning.add(section)
                    logger.warning("Directory %s is not " +
                                   "described in the configuration!",
                                   section)
                continue
            if not s:
                #
                # If the section is blank, that's OK.
                #
                if section not in section_warning:
                    section_warning.add(section)
                    logger.warning("Directory %s is not configured!", section)
                continue
            #
            # Now check if it is mapped.
            #
            mapped = 0
            for r in s:
                if r[0].pattern not in pattern_used:
                    pattern_used[r[0].pattern] = 0
                m = r[0].match(f)
                if m is not None:
                    pattern_used[r[0].pattern] += 1
                    reName = r[0].sub(r[1], f)
                    if reName not in hpss_files:
                        if reName in missing:
                            missing[reName]['files'].append(f)
                            missing[reName]['size'] += int(row['Size'])
                        else:
                            missing[reName] = {'files': [f],
                                               'size': int(row['Size'])}
                    logger.debug("%s in %s.", f, reName)
                    mapped += 1
            if mapped == 0:
                logger.error("%s is not mapped to any file on HPSS!", f)
                nmissing += 1
            if mapped > 1:
                logger.error("%s is mapped to multiple files on HPSS!", f)
                nmultiple += 1
            if (nfiles % report) == 0:
                logger.info("%9d files scanned.", nfiles)
    with open(missing_files, 'w') as fp:
        json.dump(missing, fp, indent=2, separators=(',', ': '))
    if nmissing > 0:
        logger.critical("Not all files would be backed up with " +
                        "this configuration!")
        return False
    if nmultiple > 0:
        logger.critical("Some files would be backed up more than " +
                        "once with this configuration!")
        return False
    for p in pattern_used:
        if pattern_used[p] == 0:
            logger.critical("Pattern '%s' was never used!", p)
            return False
    nbackups = 0
    for k in missing:
        logger.info('%s is %d bytes.', k, missing[k]['size'])
        nbackups += len(missing[k]['files'])
        if missing[k]['size']/1024/1024/1024 > limit:
            logger.critical("HPSS file %s would be too large!", k)
            return False
    if nbackups > 0:
        logger.info('%d files selected for backup.', nbackups)
    return (nmissing == 0) and (nmultiple == 0)


def process_missing(missing_cache, disk_root, hpss_root, dirmode='2770',
                    test=False):
    """Convert missing files into HPSS commands.

    Parameters
    ----------
    missing_cache : :class:`str`
        Name of a JSON file containing the missing file data.
    disk_root : :class:`str`
        Missing files are relative to this root on disk.
    hpss_root : :class:`str`
        Missing files are relative to this root on HPSS.
    dirmode : :class:`str`, optional
        Create directories on HPSS with this mode (default ``drwxrws---``).
    test : :class:`bool`, optional
        Test mode.  Try not to make any changes.
    """
    import logging
    import json
    from os import chdir, getcwd, remove
    from os.path import basename, dirname, join
    from .os import makedirs
    from .util import get_tmpdir, hsi, htar
    logger = logging.getLogger(__name__ + '.process_missing')
    logger.debug("Processing missing files from %s.", missing_cache)
    with open(missing_cache) as fp:
        missing = json.load(fp)
    created_directories = set()
    start_directory = getcwd()
    for h in missing:
        h_file = join(hpss_root, h)
        if h.endswith('.tar'):
            if h.endswith('_files.tar'):
                disk_chdir = dirname(h)
                Lfile = join(get_tmpdir(), basename(h.replace('.tar', '.txt')))
                htar_dir = None
                Lfile_lines = ('\n'.join([basename(f)
                                          for f in missing[h]['files']]) +
                               '\n')
                if test:
                    logger.debug(Lfile_lines)
                else:
                    with open(Lfile, 'w') as fp:
                        fp.write(Lfile_lines)
            else:
                disk_chdir = dirname(h)
                Lfile = None
                htar_dir = basename(h).split('_')[-1].split('.')[0]
            logger.debug("chdir('%s')", join(disk_root, disk_chdir))
            chdir(join(disk_root, disk_chdir))
            h_dir = join(hpss_root, disk_chdir)
            if h_dir not in created_directories:
                logger.debug("makedirs('%s', mode='%s')", h_dir, dirmode)
                if not test:
                    makedirs(h_dir, mode=dirmode)
                created_directories.add(h_dir)
            if Lfile is None:
                logger.debug("htar('-cvf', '%s', '-H', " +
                             "'crc:verify=all', '%s')", h_file, htar_dir)
                if test:
                    out, err = ('Test mode, skipping htar command.', '')
                else:
                    out, err = htar('-cvf', h_file, '-H', 'crc:verify=all',
                                    htar_dir)
            else:
                logger.debug("htar('-cvf', '%s', '-H', 'crc:verify=all', " +
                             "'-L', '%s')", h_file, Lfile)
                if test:
                    out, err = ('Test mode, skipping htar command.', '')
                else:
                    out, err = htar('-cvf', h_file, '-H', 'crc:verify=all',
                                    '-L', Lfile)
            logger.debug(out)
            if err:
                logger.warn(err)
            if Lfile is not None:
                logger.debug("remove('%s')", Lfile)
                if not test:
                    remove(Lfile)
        else:
            if dirname(h_file) not in created_directories:
                logger.debug("makedirs('%s', mode='%s')", dirname(h_file),
                             dirmode)
                if not test:
                    makedirs(dirname(h_file), mode=dirmode)
                created_directories.add(dirname(h_file))
            logger.debug("hsi('put', '%s', ':', '%s')",
                         join(disk_root, missing[h]['files'][0]), h_file)
            if test:
                out = "Test mode, skipping hsi command."
            else:
                out = hsi('put', join(disk_root, missing[h]['files'][0]),
                          ':', h_file)
            logger.debug(out)
    chdir(start_directory)
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
        logger.debug("Using existing file cache: %s", disk_files_cache)
        return True
    else:
        logger.info("No disk cache file, starting scan.")
        with open(disk_files_cache, 'w') as t:
            t.write('Name,Size\n')
            try:
                for disk_root in disk_roots:
                    logger.debug("Starting os.walk at %s.", disk_root)
                    for root, dirs, files in os.walk(disk_root):
                        logger.debug("Scanning disk directory %s.", root)
                        for f in files:
                            fullname = join(root, f)
                            if not islink(fullname):
                                cachename = fullname.replace(disk_root+'/', '')
                                size = os.stat(fullname).st_size
                                t.write("{0},{1:d}\n".format(cachename, size))
            except OSError:
                logger.error('Exception encountered while creating ' +
                             'disk cache file!')
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
        logger.info("Found cache file %s.", hpss_files_cache)
        with open(hpss_files_cache) as t:
            hpss_files = [l.strip() for l in t.readlines()]
    else:
        logger.info("No HPSS cache file, starting scan at %s.", hpss_root)
        hpss_files = list()
        for root, dirs, files in walk(hpss_root):
            # hpss_files += [f.path.replace(hpss_root+'/','')
            #                for f in files if not f.ishtar]
            logger.debug("Scanning HPSS directory %s.", root)
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


def physical_disks(release_root, config):
    """Convert a root path into a list of physical disks containing data.

    Parameters
    ----------
    release_root : :class:`str`
        The "official" path to the data.
    config : :class:`dict`
        A dictionary containing path information.

    Returns
    -------
    :func:`tuple`
        A tuple containing the physical disk paths.
    """
    from os.path import basename, join
    try:
        pd = config['physical_disks']
    except KeyError:
        return (release_root,)
    if not pd:
        return (release_root,)
    broot = basename(config['root'])
    if ((len(pd) == 1) and (pd[0] == broot)):
        return (release_root,)
    if pd[0].startswith('/'):
        return tuple([join(d, basename(release_root)) for d in pd])
    return tuple([release_root.replace(broot, d) for d in pd])


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
    from os import environ
    from os.path import basename, join, splitext
    from . import __version__ as hpsspyVersion
    #
    # Options
    #
    desc = 'Verify the presence of files on HPSS.'
    parser = ArgumentParser(prog=basename(argv[0]), description=desc)
    parser.add_argument('-c', '--cache-dir', action='store', dest='cache',
                        metavar='DIR',
                        default=join(environ['HOME'], 'scratch'),
                        help=('Write cache files to DIR (Default: ' +
                              '%(default)s).'))
    parser.add_argument('-D', '--clobber-disk', action='store_true',
                        dest='clobber_disk',
                        help='Ignore any existing disk cache files.')
    parser.add_argument('-H', '--clobber-hpss', action='store_true',
                        dest='clobber_hpss',
                        help='Ignore any existing HPSS cache files.')
    parser.add_argument('-l', '--size-limit', action='store', type=float,
                        dest='limit', metavar='N', default=1024.0,
                        help=("Do not allow archive files larger than " +
                              "N GB (Default: %(default)s GB)."))
    parser.add_argument('-p', '--process', action='store_true',
                        dest='process',
                        help=('Process the list of missing files to produce ' +
                              'HPSS commands.'))
    parser.add_argument('-r', '--report', action='store', type=int,
                        dest='report', metavar='N', default=10000,
                        help=("Print an informational message after " +
                              "every N files (Default: %(default)s)."))
    parser.add_argument('-t', '--test', action='store_true',
                        dest='test',
                        help="Test mode. Try not to make any changes.")
    parser.add_argument('-v', '--verbose', action='store_true',
                        dest='verbose',
                        help="Increase verbosity. Increase it a lot.")
    parser.add_argument('-V', '--version', action='version',
                        version="%(prog)s " + hpsspyVersion)
    parser.add_argument('config', metavar='FILE',
                        help="Read configuration from FILE.")
    parser.add_argument('release', metavar='SECTION',
                        help="Read SECTION from the configuration file.")
    options = parser.parse_args()
    #
    # Logging
    #
    ll = logging.WARNING
    if options.test:
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
    status = validate_configuration(options.config)
    if status > 0:
        return status
    hpss_map, config = files_to_hpss(options.config, options.release)
    release_root = join(config['root'], options.release)
    hpss_release_root = join(config['hpss_root'], options.release)
    #
    # Read HPSS files and cache.
    #
    if options.test:
        logger.info("Test mode. Pretending no files exist on HPSS.")
        hpss_files = frozenset([])
    else:
        logger.debug("Cache files will be written to %s.", options.cache)
        hpss_files_cache = join(options.cache,
                                'hpss_files_{0}.txt'.format(options.release))
        logger.debug("hpss_files_cache = '%s'", hpss_files_cache)
        hpss_files = scan_hpss(hpss_release_root, hpss_files_cache,
                               clobber=options.clobber_hpss)
    #
    # Read disk files and cache.
    #
    disk_files_cache = join(options.cache,
                            'disk_files_{0}.csv'.format(options.release))
    logger.debug("disk_files_cache = '%s'", disk_files_cache)
    disk_roots = physical_disks(release_root, config)
    status = scan_disk(disk_roots, disk_files_cache,
                       clobber=options.clobber_disk)
    if not status:
        return 1
    #
    # See if the files are on HPSS.
    #
    missing_files_cache = join(options.cache,
                               ('missing_files_' +
                                '{0}.json').format(options.release))
    logger.debug("missing_files_cache = '%s'", missing_files_cache)
    status = find_missing(hpss_map, hpss_files, disk_files_cache,
                          missing_files_cache, options.report, options.limit)
    if not status:
        return 1
    #
    # Post process to generate HPSS commands
    #
    if options.process or options.test:
        process_missing(missing_files_cache, release_root, hpss_release_root,
                        test=options.test)
    return 0
