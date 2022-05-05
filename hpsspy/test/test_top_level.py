# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_top_level
~~~~~~~~~~~~~~~~~~~~~~~~~~

Test top-level hpsspy functions.
"""
import re
from .. import __version__ as theVersion


versionRE = re.compile(r'([0-9]+!)?([0-9]+)(\.[0-9]+)*((a|b|rc|\.post|\.dev)[0-9]+)?')


def test_version():
    """Ensure the version conforms to PEP386/PEP440.
    """
    assert versionRE.match(theVersion)
