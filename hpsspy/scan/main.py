# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Verify the presence of files on HPSS.
"""
#
def main():
    """Main program.
    """
    import os
    import logging
    from argparse import ArgumentParser
    from sys import argv
    from os import getenv
    from os.path import basename, join
    from hpsspy.scan import compile_map, files_to_hpss, find_missing, scan_disk, scan_hpss
    #
    # Options
    #
    parser = ArgumentParser(description=__doc__,prog=basename(argv[0]))
    parser.add_argument('-c', '--clobber-disk', action='store_true', dest='clobber_disk',
        help='Ignore any existing disk cache files.')
    parser.add_argument('-C', '--clobber-hpss', action='store_true', dest='clobber_hpss',
        help='Ignore any existing HPSS cache files.')
    parser.add_argument('-r', '--report', action='store', type=int, metavar='N',
        dest='report', default=10000,
        help="Print an informational message after every N files.")
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
        help="Increase verbosity.")
    parser.add_argument('config',metavar='FILE',
        help="Read configuration from FILE.")
    parser.add_argument('release',metavar='SECTION',
        help="Read SECTION from the configuration file.")
    options = parser.parse_args()
    #
    # Logging
    #
    ll = logging.INFO
    if options.verbose:
        ll = logging.DEBUG
    logging.basicConfig(level=ll, format='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%Y-%m-%dT%H:%M:%S')
    logger = logging.getLogger(__name__)
    #
    # Config file
    #
    if options.config not in ('sdss','desi'):
        logger.error('Unsupported configuration: {0}'.format(options.config))
        return 1
    hpss_map, config = files_to_hpss(options.config+'.json',options.release)
    release_root = join(config['root'],options.release)
    hpss_release_root = join(config['hpss_root'],options.release)
    #
    # Read HPSS files and cache.
    #
    hpss_files_cache = join(getenv('HOME'),'scratch','hpss_files_{0}.txt'.format(options.release))
    logger.debug('HPSS file cache = {0}'.format(hpss_files_cache))
    hpss_files = scan_hpss(hpss_release_root,hpss_files_cache,clobber=options.clobber_hpss)
    #
    # Read disk files and cache.
    #
    disk_files_cache = join(getenv('HOME'),'scratch','disk_files_{0}.txt'.format(options.release))
    logger.debug('Disk file cache = {0}'.format(disk_files_cache))
    disk_roots = [release_root.replace(basename(release_root),d) for d in config['physical_disks']]
    status = scan_disk(disk_roots,disk_files_cache,clobber=options.clobber_disk)
    if not status:
        return 1
    #
    # See if the files are on HPSS.
    #
    missing = find_missing(hpss_map,hpss_files,disk_files_cache,options.report)
    return 0
