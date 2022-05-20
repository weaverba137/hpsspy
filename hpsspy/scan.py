# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.scan
~~~~~~~~~~~

Functions for scanning directory trees to find files in need of backup.
"""
import csv
import json
import logging
import os
import re
import sys
from argparse import ArgumentParser
from pkg_resources import resource_exists, resource_stream
from . import __version__ as hpsspyVersion
from .os import makedirs, walk
from .util import get_tmpdir, hsi, htar


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
    logger = logging.getLogger(__name__ + '.files_to_hpss')
    foo, xtn = os.path.splitext(os.path.basename(config))
    if xtn != '.json':
        logger.warning("%s might not be a JSON file!", config)
    try:
        with open(config) as fp:
            try:
                json_data = json.load(fp)
            # except json.JSONDecodeError:
            except ValueError:
                logger.critical("%s is not valid JSON.", config)
                return 1
    # except FileNotFoundError:
    except IOError:
        logger.critical("%s does not exist. Try again.", config)
        return 1
    if '__config__' in json_data:
        for k in ('root', 'hpss_root', 'physical_disks'):
            if k not in json_data['__config__']:
                logger.warning("%s '__config__' section does not contain an " +
                               "entry for '%s'.", config, k)
    else:
        logger.critical("%s does not contain a '__config__' section.", config)
        return 1
    for k in json_data:
        if k == '__config__':
            continue
        if '__exclude__' not in json_data[k]:
            logger.warning("Section '%s' should at least have an " +
                           "'__exclude__' entry.", k)
        try:
            new_map = compile_map(json_data, k)
        except re.error:
            logger.critical("Regular Expression error detected in " +
                            "section '%s'!", k)
            return 1
    return 0


def compile_map(old_map, section):
    """Compile the regular expressions in a map.

    Parameters
    ----------
    old_map : :class:`dict`
        A dictionary containing regular expressions to compile.
    section : :class:`str`
        An initial key to determine the section of the dictionary of interest.
        Typically, this will be a top-level directory.

    Returns
    -------
    :class:`dict`
        A new dictionary containing compiled regular expressions.
    """
    new_map = dict()
    for key in old_map[section]:
        if key == '__exclude__':
            new_map[key] = frozenset(old_map[section][key])
        else:
            foo = list()
            for r in old_map[section][key]:
                foo.append((re.compile(r), old_map[section][key][r]))
            new_map[key] = tuple(foo)
    return new_map


def files_to_hpss(hpss_map_cache, section):
    """Create a map of files on disk to HPSS files.

    Parameters
    ----------
    hpss_map_cache : :class:`str`
        Data file containing the map.
    section : :class:`str`
        An initial key to determine the section of the dictionary of interest.
        Typically, this will be a top-level directory.

    Returns
    -------
    :func:`tuple`
        A tuple contiaining the compiled mapping and an additional
        configuration dictionary.
    """
    logger = logging.getLogger(__name__ + '.files_to_hpss')
    if os.path.exists(hpss_map_cache):
        logger.info("Found map file %s.", hpss_map_cache)
        with open(hpss_map_cache) as t:
            hpss_map = json.load(t)
    else:
        if resource_exists('hpsspy', 'data/' + hpss_map_cache):
            logger.info("Reading from file %s in the hpsspy distribution.",
                        hpss_map_cache)
            t = resource_stream('hpsspy', 'data/' + hpss_map_cache)
            hpss_map = json.loads(t.read().decode())
            t.close()
        else:
            logger.warning("Returning empty map file!")
            hpss_map = {"__config__": {},
                        "dr8": {"__exclude__": [], "casload": {},
                                "apogee": {}, "boss": {}, "sdss": {}},
                        "dr9": {"__exclude__": [], "casload": {},
                                "apogee": {}, "boss": {}, "sdss": {}},
                        "dr10": {"__exclude__": [], "casload": {},
                                 "apogee": {}, "boss": {}, "sdss": {}},
                        "dr11": {"__exclude__": [], "casload": {},
                                 "apogee": {}, "boss": {}, "marvels": {},
                                 "sdss": {}},
                        "dr12": {"__exclude__": [], "casload": {}, "apo": {},
                                 "apogee": {}, "boss": {}, "marvels": {},
                                 "sdss": {}}}
    return (compile_map(hpss_map, section), hpss_map['__config__'])


def find_missing(hpss_map, hpss_files, disk_files_cache, missing_files,
                 report=10000, limit=1024.0):
    """Compare HPSS files to disk files.

    Parameters
    ----------
    hpss_map : :class:`dict`
        A mapping of file names to HPSS files.
    hpss_files : :class:`dict`
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
    logger = logging.getLogger(__name__ + '.find_missing')
    nfiles = 0
    nmissing = 0
    nmultiple = 0
    backups = dict()
    pattern_used = dict()
    section_warning = set()
    with open(disk_files_cache, newline='') as t:
        reader = csv.DictReader(t)
        for row in reader:
            f = row['Name']
            nfiles += 1
            if f in hpss_map["__exclude__"]:
                logger.info("%s is excluded.", f)
                continue
            section = f.split('/')[0]
            if section == f:
                #
                # Top-level section containing no subdirectories.
                #
                section = '__top__'
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
                    mapped += 1
                    if r[1] == "EXCLUDE":
                        logger.debug("%s is excluded from backups.", f)
                    elif r[1] == "AUTOMATED":
                        logger.debug("%s is backed up by some other " +
                                     "automated process.", f)
                    else:
                        reName = r[0].sub(r[1], f)
                        logger.debug("%s in %s.", f, reName)
                        exists = reName in hpss_files
                        if exists:
                            newer = int(row['Mtime']) > hpss_files[reName][1]
                        else:
                            newer = False
                        if newer:
                            logger.warning("%s is newer than %s, " +
                                           "marking as missing!",
                                           f, reName)
                        if reName in backups:
                            backups[reName]['files'].append(f)
                            backups[reName]['size'] += int(row['Size'])
                            #
                            # 'newer' can change from False to True, but
                            # it should never change back to False.
                            #
                            if newer:
                                backups[reName]['newer'] = newer
                        else:
                            backups[reName] = {'files': [f],
                                               'size': int(row['Size']),
                                               'newer': newer,
                                               'exists': exists}
            if mapped == 0:
                logger.error("%s is not mapped to any file on HPSS!", f)
                nmissing += 1
            if mapped > 1:
                logger.error("%s is mapped to multiple files on HPSS!", f)
                nmultiple += 1
            if (nfiles % report) == 0:
                logger.info("%9d files scanned.", nfiles)
    for p in pattern_used:
        if pattern_used[p] == 0:
            logger.info("Pattern '%s' was never used, " +
                        "maybe files have been removed from disk?", p)
    #
    # Eliminate backups that exist and have no newer files on disk.
    #
    missing = dict()
    nbackups = 0
    for k, v in backups.items():
        if v['exists'] and not v['newer']:
            logger.debug("%s is a valid backup.", k)
        else:
            logger.info('%s is %d bytes.', k, v['size'])
            if v['size']/1024/1024/1024 > limit:
                logger.error("HPSS file %s would be too large, " +
                             "skipping backup!", k)
            else:
                logger.debug("Adding %s to missing backups.", k)
                nbackups += len(v['files'])
                missing[k] = v
    if nbackups > 0:
        logger.info('%d files selected for backup.', nbackups)
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
    logger = logging.getLogger(__name__ + '.process_missing')
    logger.debug("Processing missing files from %s.", missing_cache)
    with open(missing_cache) as fp:
        missing = json.load(fp)
    created_directories = set()
    start_directory = os.getcwd()
    for h in missing:
        h_file = os.path.join(hpss_root, h)
        if h.endswith('.tar'):
            disk_chdir = os.path.dirname(h)
            full_chdir = os.path.join(disk_root, disk_chdir)
            if h.endswith('_files.tar'):
                Lfile = os.path.join(get_tmpdir(),
                                     os.path.basename(h.replace('.tar',
                                                                '.txt')))
                htar_dir = None
                Lfile_lines = ('\n'.join([os.path.basename(f)
                                          for f in missing[h]['files']]) +
                               '\n')
                if test:
                    logger.debug(Lfile_lines)
                else:
                    with open(Lfile, 'w') as fp:
                        fp.write(Lfile_lines)
            else:
                Lfile = None
                #
                # Be careful, because the directory name may itself
                # contain underscore characters, or X characters.
                #
                b = extract_directory_name(h)
                htar_dir = []
                if os.path.isdir(os.path.join(full_chdir, b)):
                    htar_dir = [b]
                elif b.endswith('X'):
                    htar_re = re.compile(b.replace('X', '.') + '$')
                    htar_dir = [d for d in os.listdir(full_chdir)
                                if os.path.isdir(os.path.join(full_chdir, d))
                                and htar_re.match(d) is not None]
                else:
                    logger.error(("Could not find directories corresponding " +
                                  "to %s!"), h)
                    continue
            logger.debug("os.chdir('%s')", full_chdir)
            os.chdir(full_chdir)
            h_dir = os.path.join(hpss_root, disk_chdir)
            if h_dir not in created_directories:
                logger.debug("makedirs('%s', mode='%s')", h_dir, dirmode)
                if not test:
                    makedirs(h_dir, mode=dirmode)
                created_directories.add(h_dir)
            if Lfile is None:
                logger.info("htar('-cvf', '%s', '-H', " +
                            "'crc:verify=all', %s)", h_file,
                            ', '.join(["'{0}'".format(h) for h in htar_dir]))
                if test:
                    out, err = ('Test mode, skipping htar command.', '')
                else:
                    out, err = htar('-cvf', h_file, '-H', 'crc:verify=all',
                                    *htar_dir)
            else:
                logger.info("htar('-cvf', '%s', '-H', 'crc:verify=all', " +
                            "'-L', '%s')", h_file, Lfile)
                if test:
                    out, err = ('Test mode, skipping htar command.', '')
                else:
                    out, err = htar('-cvf', h_file, '-H', 'crc:verify=all',
                                    '-L', Lfile)
            logger.debug(out)
            if err:
                logger.warning(err)
            if Lfile is not None:
                logger.debug("os.remove('%s')", Lfile)
                if not test:
                    os.remove(Lfile)
        else:
            d_h_file = os.path.dirname(h_file)
            if d_h_file not in created_directories:
                logger.debug("makedirs('%s', mode='%s')", d_h_file, dirmode)
                if not test:
                    makedirs(d_h_file, mode=dirmode)
                created_directories.add(d_h_file)
            logger.info("hsi('put', '%s', ':', '%s')",
                        os.path.join(disk_root, missing[h]['files'][0]),
                        h_file)
            if test:
                out = "Test mode, skipping hsi command."
            else:
                out = hsi('put',
                          os.path.join(disk_root, missing[h]['files'][0]),
                          ':', h_file)
            logger.debug(out)
    logger.debug("os.chdir('%s')", start_directory)
    os.chdir(start_directory)
    return


def extract_directory_name(filename):
    """Extract a directory name from a HTAR `filename` that may contain
    various prefixes.

    Parameters
    ----------
    filename : :class:`str`
        Name of HTAR file, including directory path.

    Returns
    -------
    :class:`str`
        Name of a directory.
    """
    d = os.path.dirname(filename)
    basefile = os.path.basename(filename).rsplit('.', 1)[0]  # remove .tar
    if not d:
        return basefile
    prefix = d.replace('/', '_') + '_'
    try:
        i = basefile.index(prefix)
    except ValueError:
        try:
            prefix = '_'.join(prefix.split('_')[1:])
            i = basefile.index(prefix)
        except ValueError:
            return basefile
    return basefile[(i + len(prefix)):]


def iterrsplit(s, c):
    """Split string `s` on `c` and rejoin on `c` from the end of `s`.

    Parameters
    ----------
    s : :class:`str`
        String to split
    c : :class:`str`
        Split on this string.

    Returns
    -------
    :class:`str`
        Iteratively return the joined parts of `s`.
    """
    ss = s.split(c)
    i = -1
    while abs(i) <= len(ss):
        yield c.join(ss[i:])
        i -= 1
    return


def scan_disk(disk_roots, disk_files_cache, overwrite=False):
    """Scan a directory tree on disk and cache the files found there.

    Parameters
    ----------
    disk_roots : :class:`list`
        Name(s) of a directory in which to start the scan.
    disk_files_cache : :class:`str`
        Name of a file to hold the cache.
    overwrite : :class:`bool`, optional
        If ``True``, ignore any existing cache files.

    Returns
    -------
    :class:`bool`
        Returns ``True`` if the cache is populated and ready to read.
    """
    logger = logging.getLogger(__name__ + '.scan_disk')
    if os.path.exists(disk_files_cache) and not overwrite:
        logger.debug("Using existing file cache: %s", disk_files_cache)
        return True
    else:
        logger.info("No disk cache file, starting scan.")
        with open(disk_files_cache, 'w', newline='') as t:
            writer = csv.writer(t)
            writer.writerow(['Name', 'Size', 'Mtime'])
            try:
                for disk_root in disk_roots:
                    logger.debug("Starting os.walk at %s.", disk_root)
                    for root, dirs, files in os.walk(disk_root):
                        logger.debug("Scanning disk directory %s.", root)
                        for f in files:
                            fullname = os.path.join(root, f)
                            if not os.path.islink(fullname):
                                cachename = fullname.replace(disk_root+'/', '')
                                s = os.stat(fullname)
                                writer.writerow([cachename,
                                                 s.st_size,
                                                 int(s.st_mtime)])
            except OSError as e:
                logger.error('Exception encountered while creating ' +
                             'disk cache file!')
                logger.error(e.strerror)
                return False
    return True


def scan_hpss(hpss_root, hpss_files_cache, overwrite=False):
    """Scan a directory on HPSS and return the files found there.

    Parameters
    ----------
    hpss_root : :class:`str`
        Name of a directory in which to start the scan.
    hpss_files_cache : :class:`str`
        Name of a file to hold the cache.
    overwrite : :class:`bool`, optional
        If ``True``, ignore any existing cache files.

    Returns
    -------
    :class:`dict`
        The set of files found on HPSS, with size and modification time.
    """
    logger = logging.getLogger(__name__ + '.scan_hpss')
    hpss_files = dict()
    if os.path.exists(hpss_files_cache) and not overwrite:
        logger.info("Found cache file %s.", hpss_files_cache)
        with open(hpss_files_cache, newline='') as t:
            reader = csv.DictReader(t)
            for row in reader:
                hpss_files[row['Name']] = (int(row['Size']), int(row['Mtime']))
    else:
        logger.info("No HPSS cache file, starting scan at %s.", hpss_root)
        with open(hpss_files_cache, 'w', newline='') as t:
            w = csv.writer(t)
            w.writerow(['Name', 'Size', 'Mtime'])
            for root, dirs, files in walk(hpss_root):
                logger.debug("Scanning HPSS directory %s.", root)
                for f in files:
                    if not f.path.endswith('.idx'):
                        ff = f.path.replace(hpss_root+'/', '')
                        hpss_files[ff] = (f.st_size, f.st_mtime)
                        w.writerow([ff, f.st_size, f.st_mtime])
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
    try:
        pd = config['physical_disks']
    except KeyError:
        return (release_root,)
    if not pd:
        return (release_root,)
    broot = os.path.basename(config['root'])
    if ((len(pd) == 1) and (pd[0] == broot)):
        return (release_root,)
    if pd[0].startswith('/'):
        return tuple([os.path.join(d, os.path.basename(release_root))
                      for d in pd])
    return tuple([release_root.replace(broot, d) for d in pd])


def _options():
    """Parse command-line options.

    Returns
    -------
    :class:`argparse.Namespace`
        The parsed command-line arguments.
    """
    desc = 'Verify the presence of files on HPSS.'
    parser = ArgumentParser(prog=os.path.basename(sys.argv[0]), description=desc)
    parser.add_argument('-c', '--cache-dir', action='store', dest='cache',
                        metavar='DIR',
                        default=os.path.join(os.environ['HOME'], 'cache'),
                        help=('Write cache files to DIR (Default: ' +
                              '%(default)s).'))
    parser.add_argument('-D', '--overwrite-disk', action='store_true',
                        dest='overwrite_disk',
                        help='Ignore any existing disk cache files.')
    parser.add_argument('-H', '--overwrite-hpss', action='store_true',
                        dest='overwrite_hpss',
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
    return parser.parse_args()


def main():
    """Entry-point for command-line scripts.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    #
    # Options
    #
    options = _options()
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
    release_root = os.path.join(config['root'], options.release)
    hpss_release_root = os.path.join(config['hpss_root'], options.release)
    #
    # Read HPSS files and cache.
    #
    if options.test:
        logger.info("Test mode. Pretending no files exist on HPSS.")
        hpss_files = dict()
    else:
        logger.debug("Cache files will be written to %s.", options.cache)
        hpss_files_cache = os.path.join(options.cache,
                                        ('hpss_files_' +
                                         '{0}.csv').format(options.release))
        logger.debug("hpss_files_cache = '%s'", hpss_files_cache)
        hpss_files = scan_hpss(hpss_release_root, hpss_files_cache,
                               overwrite=options.overwrite_hpss)
    #
    # Read disk files and cache.
    #
    disk_files_cache = os.path.join(options.cache,
                                    ('disk_files_' +
                                     '{0}.csv').format(options.release))
    logger.debug("disk_files_cache = '%s'", disk_files_cache)
    disk_roots = physical_disks(release_root, config)
    status = scan_disk(disk_roots, disk_files_cache,
                       overwrite=options.overwrite_disk)
    if not status:
        return 1
    #
    # See if the files are on HPSS.
    #
    missing_files_cache = os.path.join(options.cache,
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
