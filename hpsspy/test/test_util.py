# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
#
import unittest
# import json
# from pkg_resources import resource_exists, resource_stream
from os import environ
from hpsspy.util import get_tmpdir
#
class TestUtil(unittest.TestCase):
    def setUp(self):
        # Store the original value of TMPDIR, if present.
        self.TMPDIR = None
        if 'TMPDIR' in environ:
            self.TMPDIR = environ['TMPDIR']
    def tearDown(self):
        # Restore the original value of TMPDIR, if it was present.
        if self.TMPDIR is not None:
            environ['TMPDIR'] = self.TMPDIR
    def test_get_tmpdir(self):
        myTmpDir = '/my/own/personal/temporary/directory'
        self.assertEqual(get_tmpdir(tmpdir=myTmpDir),myTmpDir)
        if self.TMPDIR is None:
            environ['TMPDIR'] = '/Temporary/TMPDIR'
            self.assertEqual(get_tmpdir(),'/Temporary/TMPDIR')
        else:
            self.assertEqual(get_tmpdir(),self.TMPDIR)
        del environ['TMPDIR']
        self.assertEqual(get_tmpdir(),'/tmp')
#
if __name__ == '__main__':
    unittest.main()
