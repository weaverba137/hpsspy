#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst

# NOTE: The configuration for the package, including the name, version, and
# other information are set in the setup.cfg file.

import os
import sys
from importlib import import_module
from setuptools import setup

# from extension_helpers import get_extensions


# First provide helpful messages if contributors try and run legacy commands
# for tests or docs.

TEST_HELP = """
Note: running tests is no longer done using 'python setup.py test'. Instead
you will need to run:

    pytest

If you don't already have pytest installed, you can install it with:

    pip install pytest

"""

if 'test' in sys.argv:
    print(TEST_HELP)
    sys.exit(1)

DOCS_HELP = """
Note: building the documentation is no longer done using
'python setup.py build_docs'. Instead you will need to run:

    sphinx-build -W --keep-going -b html doc doc/_build/html

If you don't already have Sphinx installed, you can install it with:

    pip install Sphinx

"""

if 'build_docs' in sys.argv or 'build_sphinx' in sys.argv:
    print(DOCS_HELP)
    sys.exit(1)

module = import_module('hpsspy')
setup(version=module.__version__)
