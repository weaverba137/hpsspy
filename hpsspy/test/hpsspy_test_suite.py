"""
hpsspy.test.hpsspy_test_suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Used to initialize the unit test framework via ``python setup.py test``.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
# The line above will help with 2to3 support.
import unittest


def hpsspy_test_suite():
    """Returns unittest.TestSuite of hpsspy tests.

    This is factored out separately from runtests() so that it can be used by
    ``python setup.py test``.
    """
    return unittest.defaultTestLoader.discover('hpsspy')


def runtests():
    """Run all tests in hpsspy.test.test_*.
    """
    # Load all TestCase classes from hpsspy/test/test_*.py
    tests = hpsspy_test_suite()
    # Run them
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == "__main__":
    runtests()
