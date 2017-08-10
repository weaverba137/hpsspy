# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_os
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the os subpackage.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
import unittest
# import json
# from pkg_resources import resource_filename
import os
from ..os import chmod, lstat, stat
from ..os.path import isdir, isfile, islink
from .test_util import MockHpss


class TestOs(MockHpss):
    """Test the functions in the os subpackage.
    """

    def test_isdir(self):
        """Test the isdir() function.
        """
        pass

    def test_isfile(self):
        """Test the isfile() function.
        """
        pass

    def test_islink(self):
        """Test the islink() function.
        """
        pass


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
