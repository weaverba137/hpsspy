# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import unittest
import json
from pkg_resources import resource_exists, resource_stream
#
class TestData(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_sdss(self):
        self.assertTrue(resource_exists('hpsspy.data','sdss.json'),"Could not find sdss.json!")
        t = resource_stream('hpsspy.data','sdss.json')
        hpss_map = json.load(t)
        for release in ['dr{0:d}'.format(k) for k in range(8,13)]:
            self.assertIn(release,hpss_map,"Release {0} is not in sdss.json!".format(release))
        t.close()
#
if __name__ == '__main__':
    unittest.main()