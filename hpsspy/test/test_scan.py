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
# import json
# from pkg_resources import resource_filename
import os
from ..scan import main


class TestScan(unittest.TestCase):
    """Test the functions in the scan subpackage.
    """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # Store the original value of env variables, if present.
        # self.env = {'TMPDIR': None, 'HPSS_DIR': None}
        # for e in self.env:
        #     if e in os.environ:
        #         self.env[e] = os.environ['TMPDIR']
        pass

    def tearDown(self):
        # Restore the original value of env variables, if they were present.
        # for e in self.env:
        #     if self.env[e] is None:
        #         if e in os.environ:
        #             del os.environ[e]
        #     else:
        #         os.environ[e] = self.env[e]
        pass


def test_suite():
    """Allows testing of only this module with the command::
        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
