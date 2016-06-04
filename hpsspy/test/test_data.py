# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_data
~~~~~~~~~~~~~~~~~~~~~

Check the associated data files.
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
import unittest
import json
from pkg_resources import resource_exists, resource_stream


class TestData(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
