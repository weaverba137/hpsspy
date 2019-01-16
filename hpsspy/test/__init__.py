# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test
~~~~~~~~~~~

Used to initialize the unit test framework via ``python setup.py test``.
"""
import unittest
from os.path import dirname


def hpsspy_test_suite():
    """Returns unittest.TestSuite of hpsspy tests.

    This is factored out separately from runtests() so that it can be used by
    ``python setup.py test``.
    """
    py_dir = dirname(dirname(__file__))
    return unittest.defaultTestLoader.discover(py_dir,
                                               top_level_dir=dirname(py_dir))


def runtests():
    """Run all tests in hpsspy.test.test_*.
    """
    # Load all TestCase classes from hpsspy/test/test_*.py
    tests = hpsspy_test_suite()
    # Run them
    unittest.TextTestRunner(verbosity=2).run(tests)
