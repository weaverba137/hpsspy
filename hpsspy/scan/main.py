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
    from hpsspy.scan import compile_map, files_to_hpss, scan_disk, scan_hpss
    #
    # Options
    #
    parser = ArgumentParser(description=__doc__,prog=basename(argv[0]))
    parser.add_argument('-r', '--report', action='store', type=int, metavar='N',
        dest='report', default=10000,
        help="Print an informational message after every N files.")
    parser.add_argument('-v', '--verbose', action='store_true', dest='verbose',
        help="Increase verbosity.")
    parser.add_argument('release',metavar='RELEASE',
        help="Scan files associated with data release RELEASE.")
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
    # Check environment
    #
    if getenv('SAS_ROOT') is None:
        logger.error("SAS_ROOT is not set!  Do 'module load tree/{0}'.".format(options.release))
        return 1
    if basename(getenv('SAS_ROOT')) != options.release:
        logger.error("SAS_ROOT is inconsistent with {0}! Do 'module switch tree/{0}'.".format(options.release))
        return 1
    #
    # Read HPSS files and cache.
    #
    hpss_files_cache = join(getenv('HOME'),'scratch','hpss_files_{0}.txt'.format(options.release))
    logger.debug('HPSS file cache = {0}'.format(hpss_files_cache))
    hpss_files = scan_hpss(getenv('HPSS_ROOT'),hpss_files_cache)
    #
    # Read disk files and cache.
    #
    disk_files_cache = join(getenv('HOME'),'scratch','disk_files_{0}.txt'.format(options.release))
    logger.debug('Disk file cache = {0}'.format(disk_files_cache))
    disk_roots = [getenv('SAS_ROOT').replace('raid006',d) for d in ('raid006','raid000','raid005','raid007','raid008','raid2008','netapp')]
    status = scan_disk(disk_roots,disk_files_cache)
    if not status:
        return 1
    #
    # See if the files are on HPSS.
    #
    # hpss_map_cache = join(getenv('HPSSPY_DIR'),'data','sdss.json')
    hpss_map = files_to_hpss('sdss.json')
    missing = find_missing(hpss_map,hpss_files,disk_files_cache,options.report)
    return 0
