#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
#
# Imports
#
import sys
from os.path import exists
#
# setuptools' sdist command ignores MANIFEST.in
#
from distutils.command.sdist import sdist as DistutilsSdist
# from ez_setup import use_setuptools
# use_setuptools()
from setuptools import setup, find_packages
setup_keywords = dict()
#
# General settings.
#
setup_keywords['name'] = 'hpsspy'
setup_keywords['description'] = 'Package for interacting with HPSS.'
setup_keywords['author'] = 'Benjamin Alan Weaver'
setup_keywords['author_email'] = 'baweaver@lbl.gov'
setup_keywords['license'] = 'BSD'
setup_keywords['url'] = 'https://github.com/weaverba137/hpsspy'
setup_keywords['keywords'] = ['backup']
setup_keywords['classifiers'] = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Topic :: System :: Archiving'
    ]
#
# Import this module to get __doc__ and __version__.
#
try:
    from importlib import import_module
    product = import_module(setup_keywords['name'])
    # setup_keywords['long_description'] = product.__doc__
    setup_keywords['version'] = product.__version__
except ImportError:
    setup_keywords['version'] = '0.0.1.dev'
#
# Try to get the long description from the README.rst file.
#
if exists('README.rst'):
    with open('README.rst') as readme:
        setup_keywords['long_description'] = readme.read()
else:
    setup_keywords['long_description'] = ''
setup_keywords['download_url'] = 'https://github.com/weaverba137/hpsspy/tarball/' + setup_keywords['version']
#
# Set other keywords for the setup function.  These are automated, & should
# be left alone unless you are an expert.
#
setup_keywords['provides'] = [setup_keywords['name']]
setup_keywords['python_requires'] = '>=3.4'
setup_keywords['zip_safe'] = True
setup_keywords['use_2to3'] = False
setup_keywords['packages'] = find_packages()
setup_keywords['cmdclass'] = {'sdist': DistutilsSdist}
setup_keywords['package_data'] = {'hpsspy': ['data/*.json',],
                                  'hpsspy.test': ['t/*']}
#
# Autogenerate command-line scripts.
#
setup_keywords['entry_points'] = {
    'console_scripts': [
        'missing_from_hpss = hpsspy.scan:main',
        ]
    }
#
# Test suite
#
setup_keywords['test_suite'] = 'hpsspy.test.hpsspy_test_suite'
#
# Run setup command.
#
setup(**setup_keywords)
