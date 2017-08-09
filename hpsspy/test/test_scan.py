# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_scan
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the scan subpackage.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
import unittest
import json
from pkg_resources import resource_filename, resource_stream
import os
import sys
import re
from ..scan import compile_map, physical_disks, validate_configuration


class TestScan(unittest.TestCase):
    """Test the functions in the scan subpackage.
    """

    @classmethod
    def setUpClass(cls):
        cls.PY3 = sys.version_info[0] > 2

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
        pass

    def test_compile_map(self):
        """Test compiling regular expressions in the JSON configuration file.
        """
        new_map = compile_map(self.config, 'data')
        self.assertEqual(new_map['exclude'], frozenset(['README.html']))
        for k in self.config['data']:
            if k != 'exclude':
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
        status = validate_configuration(self.config_name)
        self.assertEqual(status, 0)


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
