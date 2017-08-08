# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_validate
~~~~~~~~~~~~~~~~~~~~~~~~~

Test the configuration validator.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
import unittest
import json
from pkg_resources import resource_exists, resource_stream
from ..validate import main

class TestValidate(unittest.TestCase):
    """Test the configuration validator.
    """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
