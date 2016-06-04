# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_util
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the util subpackage.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
import unittest
# import json
# from pkg_resources import resource_exists, resource_stream
from os import environ
from ..util import get_hpss_dir, get_tmpdir


class TestUtil(unittest.TestCase):
    """Test the functions in the util subpackage.
    """

    def setUp(self):
        # Store the original value of env variables, if present.
        self.env = {'TMPDIR': None, 'HPSS_DIR': None}
        for e in self.env:
            if e in environ:
                self.env[e] = environ['TMPDIR']

    def tearDown(self):
        # Restore the original value of env variables, if they were present.
        for e in self.env:
            if self.env[e] is None:
                if e in environ:
                    del environ[e]
            else:
                environ[e] = self.env[e]

    def test_get_hpss_dir(self):
        """Test searching for the HPSS_DIR variable.
        """
        environ['HPSS_DIR'] = '/path/to/hpss'
        self.assertEqual(get_hpss_dir(), '/path/to/hpss/bin')

    def test_get_tmpdir(self):
        """Test the TMPDIR search function.
        """
        myTmpDir = '/my/own/personal/temporary/directory'
        self.assertEqual(get_tmpdir(tmpdir=myTmpDir), myTmpDir)
        if self.env['TMPDIR'] is None:
            environ['TMPDIR'] = '/Temporary/TMPDIR'
            self.assertEqual(get_tmpdir(), '/Temporary/TMPDIR')
        else:
            self.assertEqual(get_tmpdir(), self.env['TMPDIR'])
        del environ['TMPDIR']
        self.assertEqual(get_tmpdir(), '/tmp')


if __name__ == '__main__':
    unittest.main()
