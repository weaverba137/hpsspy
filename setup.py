#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst
#
# Imports
#
import sys
from os.path import exists
from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages
setup_keywords = dict()
#
# General settings.
#
setup_keywords['name'] = 'hpsspy'
setup_keywords['description'] = 'SDSS data transfer package'
setup_keywords['author'] = 'Benjamin Alan Weaver'
setup_keywords['author_email'] = 'benjamin.weaver@nyu.edu'
setup_keywords['license'] = 'BSD'
setup_keywords['url'] = 'https://github.com/weaverba137/hpsspy'
setup_keywords['classifiers'] = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Scientific/Engineering :: Physics',
    'Topic :: Scientific/Engineering :: Astronomy',
    ],
#
# Import this module to get __doc__ and __version__.
#
try:
    from importlib import import_module
    product = import_module(setup_keywords['name'])
    setup_keywords['long_description'] = product.__doc__
    setup_keywords['version'] = product.__version__
except ImportError:
    #
    # Try to get the long description from the README.rst file.
    #
    if exists('README.rst'):
        with open('README.rst') as readme:
            setup_keywords['long_description'] = readme.read()
    else:
        setup_keywords['long_description'] = ''
    setup_keywords['version'] = '0.0.1.dev'
#
# Indicates if this version is a release version.
#
if setup_keywords['version'].endswith('dev'):
    #
    # Try to obtain svn information.
    #
    try:
        from desiUtil.install import get_svn_devstr
        setup_keywords['version'] += get_svn_devstr()
    except ImportError:
        pass
#
# Set other keywords for the setup function.  These are automated, & should
# be left alone unless you are an expert.
#
setup_keywords['provides'] = [setup_keywords['name']]
setup_keywords['requires'] = ['Python (>2.7.0)']
# setup_keywords['install_requires'] = ['Python (>2.6.0)']
setup_keywords['zip_safe'] = False # Sphinx extensions may do some introspection.
setup_keywords['use_2to3'] = True
setup_keywords['packages'] = find_packages('.')
# setup_keywords['package_dir'] = {'':'python'}
#
# Autogenerate command-line scripts.
#
setup_keywords['entry_points'] = {
    'console_scripts': [
        'missing_from_hpss = hpsspy.scan.main:main',
        ]
    }
#
# Run setup command.
#
setup(**setup_keywords)
