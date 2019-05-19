# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_scan
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the scan subpackage.
"""
import unittest
import json
import os
import sys
import re
import tempfile
import logging
from logging.handlers import MemoryHandler
from pkg_resources import resource_filename, resource_stream
from ..scan import (compile_map, files_to_hpss, physical_disks,
                    validate_configuration, process_missing, iterrsplit,
                    extract_directory_name)


class TestHandler(MemoryHandler):
    """Capture log messages in memory.
    """
    def __init__(self, capacity=1000000, flushLevel=logging.CRITICAL):
        nh = logging.NullHandler()
        MemoryHandler.__init__(self, capacity,
                               flushLevel=flushLevel, target=nh)

    def shouldFlush(self, record):
        """Never flush, except manually.
        """
        return False


class TestScan(unittest.TestCase):
    """Test the functions in the scan subpackage.
    """

    @classmethod
    def setUpClass(cls):
        logging.getLogger('hpsspy.scan').addHandler(TestHandler())
        # cls.logger.setLevel(logging.DEBUG)
        # log_format = '%(asctime)s %(name)s %(levelname)s: %(message)s'
        # logging.basicConfig(level=ll, format=log_format,
        #                     datefmt='%Y-%m-%dT%H:%M:%S')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # Store the original value of env variables, if present.
        # self.env = {'TMPDIR': None, 'HPSS_DIR': None}
        # for e in self.env:
        #     if e in os.environ:
        #         self.env[e] = os.environ['TMPDIR']
        #
        # Reload the configuration file, since we might need to manipulate it.
        #
        self.config_name = resource_filename('hpsspy.test', 't/test_scan.json')
        config_file = resource_stream('hpsspy.test', 't/test_scan.json')
        self.config = json.loads(config_file.read().decode())
        config_file.close()

    def tearDown(self):
        # Restore the original value of env variables, if they were present.
        # for e in self.env:
        #     if self.env[e] is None:
        #         if e in os.environ:
        #             del os.environ[e]
        #     else:
        #         os.environ[e] = self.env[e]
        logging.getLogger('hpsspy.scan').handlers[0].flush()

    def assertLog(self, index=-1, message=''):
        """Examine the log messages.
        """
        logger = logging.getLogger('hpsspy.scan')
        self.assertEqual(logger.handlers[0].buffer[index].getMessage(),
                         message)

    def test_iterrsplit(self):
        """Test reverse re-joining a string.
        """
        results = ['d', 'c_d', 'b_c_d', 'a_b_c_d']
        for i, s in enumerate(iterrsplit('a_b_c_d', '_')):
            self.assertEqual(s, results[i])

    def test_compile_map(self):
        """Test compiling regular expressions in the JSON configuration file.
        """
        new_map = compile_map(self.config, 'data')
        self.assertEqual(new_map['__exclude__'], frozenset(['README.html']))
        for k in self.config['data']:
            if k != '__exclude__':
                for l in new_map[k]:
                    self.assertIn(l[0].pattern, self.config['data'][k])
                    self.assertEqual(l[1],
                                     self.config['data'][k][l[0].pattern])
        #
        # Catch bad compiles
        #
        self.config['redux']['d1'] = {'d1/(r\\d{5,4})/.*$': 'd1/d1_\\1.tar'}
        with self.assertRaises(re.error) as err:
            new_map = compile_map(self.config, 'redux')
            self.assertEqual(err.colno, 8)

    def test_files_to_hpss(self):
        """Test conversion of JSON files to directory dictionary.
        """
        hpss_map, config = files_to_hpss(self.config_name, 'data')
        self.assertEqual(config['root'], '/temporary')
        for key in hpss_map['d2']:
            self.assertIn(key[0].pattern, self.config['data']['d2'])
            self.assertEqual(key[1], self.config['data']['d2'][key[0].pattern])
        hpss_map, config = files_to_hpss('desi.json', 'datachallenge')
        desi_map = {"dc2/batch/.*$": "dc2/batch.tar",
                    "dc2/([^/]+\\.txt)$": "dc2/\\1",
                    "dc2/templates/[^/]+$": "dc2/templates/templates_files.tar"
                    }
        for key in hpss_map['dc2']:
            self.assertIn(key[0].pattern, desi_map)
            self.assertEqual(key[1], desi_map[key[0].pattern])
        hpss_map, config = files_to_hpss('foo.json', 'dr8')
        self.assertIn('casload', hpss_map)

    def test_physical_disks(self):
        """Test physical disk path setup.
        """
        release_root = '/foo/bar/baz/data'
        config = {'root': '/foo/bar/baz'}
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, (release_root,))
        config['physical_disks'] = None
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, (release_root,))
        config['physical_disks'] = False
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, (release_root,))
        config['physical_disks'] = []
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, (release_root,))
        config['physical_disks'] = ['baz']
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, (release_root,))
        config['physical_disks'] = ['baz0', 'baz1', 'baz2']
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, ('/foo/bar/baz0/data',
                              '/foo/bar/baz1/data',
                              '/foo/bar/baz2/data'))
        config['physical_disks'] = ['/foo/bar0/baz',
                                    '/foo/bar1/baz',
                                    '/foo/bar2/baz']
        pd = physical_disks(release_root, config)
        self.assertEqual(pd, ('/foo/bar0/baz/data',
                              '/foo/bar1/baz/data',
                              '/foo/bar2/baz/data'))

    def test_validate_configuration(self):
        """Test the configuration file validator.
        """
        # Non-existent file
        status = validate_configuration('foo.bar')
        self.assertEqual(status, 1)
        self.assertLog(-2, "foo.bar might not be a JSON file!")
        self.assertLog(-1, "foo.bar does not exist. Try again.")
        # invalid file
        invalid = resource_filename('hpsspy.test', 't/invalid_file')
        status = validate_configuration(invalid)
        self.assertEqual(status, 1)
        self.assertLog(-2, "{0} might not be a JSON file!".format(invalid))
        self.assertLog(-1, "{0} is not valid JSON.".format(invalid))
        # Valid file
        status = validate_configuration(self.config_name)
        self.assertEqual(status, 0)
        # Valid file but missing some pieces
        c = self.config.copy()
        del c['__config__']
        fn, tmp = tempfile.mkstemp(suffix='.json')
        with open(tmp, 'w') as fd:
            json.dump(c, fd)
        status = validate_configuration(tmp)
        self.assertEqual(status, 1)
        self.assertLog(-1, ("{0} does not contain a " +
                            "'__config__' section.").format(tmp))
        os.close(fn)
        os.remove(tmp)
        c = self.config.copy()
        del c['__config__']['physical_disks']
        fn, tmp = tempfile.mkstemp(suffix='.json')
        with open(tmp, 'w') as fd:
            json.dump(c, fd)
        status = validate_configuration(tmp)
        self.assertEqual(status, 0)
        self.assertLog(-1, ("{0} '__config__' section does not contain an " +
                            "entry for '{1}'.").format(tmp, 'physical_disks'))
        os.close(fn)
        os.remove(tmp)
        c = self.config.copy()
        del c['redux']['__exclude__']
        fn, tmp = tempfile.mkstemp(suffix='.json')
        with open(tmp, 'w') as fd:
            json.dump(c, fd)
        status = validate_configuration(tmp)
        self.assertEqual(status, 0)
        self.assertLog(-1, ("Section '{0}' should at least have an " +
                            "'__exclude__' entry.").format('redux'))
        os.close(fn)
        os.remove(tmp)
        c = self.config.copy()
        c['redux']['d1'] = {'d1/(r\\d{5,4})/.*$': 'd1/d1_\\1.tar'}
        fn, tmp = tempfile.mkstemp(suffix='.json')
        with open(tmp, 'w') as fd:
            json.dump(c, fd)
        status = validate_configuration(tmp)
        self.assertEqual(status, 1)
        self.assertLog(-1, ("Regular Expression error detected in " +
                            "section '{0}'!").format('redux'))
        os.close(fn)
        os.remove(tmp)

    def test_process_missing(self):
        """Test conversion of missing files into HPSS commands.
        """
        pass

    def test_extract_directory_name(self):
        """Test conversion of HTAR file name back into directory name.
        """
        d = extract_directory_name(('images/fpc_analysis/' +
                                    'protodesi_images_fpc_analysis_' +
                                    'stability_dither-33022.tar'))
        self.assertEqual(d, 'stability_dither-33022')
        d = extract_directory_name(('buzzard/buzzard_v1.6_desicut/8/' +
                                    'buzzard_v1.6_desicut_8_7.tar'))
        self.assertEqual(d, '7')
        d = extract_directory_name('foo/bar/batch.tar')
        self.assertEqual(d, 'batch')
        d = extract_directory_name('batch.tar')
        self.assertEqual(d, 'batch')


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
