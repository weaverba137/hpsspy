# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_data
~~~~~~~~~~~~~~~~~~~~~

Check the associated data files.
"""
import unittest
import json
from pkg_resources import resource_exists, resource_stream


class TestData(unittest.TestCase):
    """Check integrity of data files.
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

    def check_json(self, filename, sections):
        """Check a generic JSON file.
        """
        res_filename = 'data/{0}'.format(filename)
        self.assertTrue(resource_exists('hpsspy', res_filename),
                        "Could not find {0}!".format(filename))
        t = resource_stream('hpsspy', res_filename)
        j = t.read()
        t.close()
        try:
            hpss_map = json.loads(j)
        except TypeError:
            hpss_map = json.loads(j.decode('utf8'))
        for s in sections:
            self.assertIn(s, hpss_map,
                          "Release {0} is not in {1}!".format(s, filename))

    def test_sdss(self):
        """Test SDSS data file.
        """
        releases = ['dr{0:d}'.format(k) for k in range(8, 13)]
        self.check_json('sdss.json', releases)

    def test_desi(self):
        """Test DESI data file.
        """
        releases = ('datachallenge', 'imaging', 'mocks', 'release',
                    'spectro', 'target')
        self.check_json('desi.json', releases)


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
