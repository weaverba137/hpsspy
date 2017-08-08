# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.validate
~~~~~~~~~~~~~~~

Functions for testing the validity of backup configurations before
actually running the backup.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def main():
    """Entry-point for command-line scripts.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    import logging
    import re
    import json
    from os import environ
    from os.path import basename, exists, isdir, join, splitext
    from sys import argv
    from argparse import ArgumentParser
    from . import __version__ as hpsspyVersion
    from .scan import compile_map, process_missing, scan_disk
    desc = 'Validate HPSS backup configuration.'
    parser = ArgumentParser(prog=basename(argv[0]), description=desc)
    parser.add_argument('-c', '--cache-dir', action='store', dest='cache',
                        metavar='DIR',
                        default=join(environ['HOME'], 'scratch'),
                        help=('Write cache files to DIR (Default: ' +
                              '%(default)s).'))
    parser.add_argument('-D', '--clobber-disk', action='store_true',
                        dest='clobber_disk',
                        help='Ignore any existing disk cache files.')
    parser.add_argument('-r', '--report', action='store', type=int,
                        dest='report', metavar='N', default=10000,
                        help=("Print an informational message after " +
                              "every N files (Default: %(default)s)."))
    parser.add_argument('-s', '--scan-files', action='store',
                        metavar='RELEASE',
                        dest='release',
                        help=('Validate the configuration file against ' +
                              'files on disk (might be slow!).'))
    parser.add_argument('-v', '--verbose', action='store_true',
                        dest='verbose',
                        help="Increase verbosity.")
    parser.add_argument('-V', '--version', action='version',
                        version="%(prog)s " + hpsspyVersion)
    parser.add_argument('config', metavar='FILE',
                        help="Read configuration from FILE.")
    options = parser.parse_args()
    #
    # Logging
    #
    ll = logging.INFO
    # if options.test or options.verbose:
    if options.verbose:
        ll = logging.DEBUG
    log_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
    logging.basicConfig(level=ll, format=log_format,
                        datefmt='%Y-%m-%dT%H:%M:%S')
    logger = logging.getLogger(__name__)
    #
    # Test validity of JSON file.
    #
    foo, xtn = splitext(basename(options.config))
    if xtn != '.json':
        logger.warn("%s might not be a JSON file!", options.config)
    try:
        with open(options.config) as fp:
            try:
                json_data = json.load(fp)
            except json.JSONDecodeError:
                logger.critical("%s is not valid JSON.", options.config)
                return 1
    except FileNotFoundError:
        logger.critical("%s does not exist. Try again.", options.config)
        return 1
    if 'config' in json_data:
        for k in ('root', 'hpss_root', 'physical_disks'):
            if k not in json_data['config']:
                logger.warning("%s 'config' section does not contain an " +
                               "entry for '%s'.", options.config, k)
    else:
        logger.error("%s does not contain a 'config' section.", options.config)
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
    #
    # Now check the JSON file against files on disk.
    #
    if options.release:
        logger.info("You have chosen to validate the configuration " +
                    "of '%s' against files on disk.  This could be slow.",
                    options.release)
        hpss_map = compile_map(json_data, options.release)
        config = json_data['config']
        release_root = join(config['root'], options.release)
        hpss_release_root = join(config['hpss_root'], options.release)
        if isdir(release_root):
            #
            # Read disk files and cache.
            #
            disk_files_cache = join(options.cache,
                                    ('disk_files_' +
                                     '{0}.txt').format(options.release))
            logger.debug("disk_files_cache = '%s'", disk_files_cache)
            disk_roots = [release_root.replace(basename(config['root']), d)
                          for d in config['physical_disks']]
            status = scan_disk(disk_roots, disk_files_cache,
                               clobber=options.clobber_disk)
            if not status:
                return 1
            #
            # Now that we've got the disk cache, assume HPSS is empty, and
            # make sure all files get backed up.
            #
            nfiles = 0
            nmissing = 0
            mapped_to_hpss = dict()
            with open(disk_files_cache) as t:
                for l in t:
                    f = l.strip()
                    if f in hpss_map["exclude"]:
                        logger.info("%s skipped.", f)
                    else:
                        section = f.split('/')[0]
                        try:
                            s = hpss_map[section]
                        except KeyError:
                            #
                            # If the section is not described, that's not
                            # good, but continue.
                            #
                            logger.error("%s is in a directory not " +
                                         "described in the configuration!",
                                         f)
                            continue
                        #
                        # If the section is blank, that's OK.
                        #
                        if not s:
                            logger.info("%s is in a directory not yet" +
                                        "configured.",
                                        f)
                            continue
                        #
                        # Now check if it is mapped.
                        #
                        mapped = False
                        for r in s:
                            m = r[0].match(f)
                            if m is not None:
                                reName = r[0].sub(r[1], f)
                                if reName in mapped_to_hpss:
                                    mapped_to_hpss[reName].append(f)
                                else:
                                    mapped_to_hpss[reName] = [f]
                                mapped = True
                                logger.debug("%s in %s.", f, reName)
                                break
                        if not mapped:
                            logger.error("%s is not mapped to any file on " +
                                         "HPSS!", f)
                            nmissing += 1
                    nfiles += 1
                    if (nfiles % options.report) == 0:
                        logger.info("%9d files scanned.", nfiles)
            missing_files_cache = join(options.cache,
                                       ('missing_files_{0}' +
                                        '.json').format(options.release))
            logger.debug("missing_files_cache = '%s'", missing_files_cache)
            with open(missing_files_cache, 'w') as fp:
                json.dump(mapped_to_hpss, fp, indent=2, separators=(',', ': '))
            if nmissing > 0:
                logger.critical("Not all files would be backed up with " +
                                "this configuration!")
                return 1
            #
            # All files map to a file on HPSS, so print out the commands
            # that would do a full backup.
            #
            logger.setLevel(logging.DEBUG)
            process_missing(missing_files_cache, release_root,
                            hpss_release_root, test=True)
        else:
            logger.critical("%s does not exist!", release_root)
            return 1
    return 0
