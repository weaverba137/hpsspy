# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_data
~~~~~~~~~~~~~~~~~~~~~

Check the associated data files.
"""
import pytest
import json
from pkg_resources import resource_exists, resource_stream


parameters = [('sdss.json', 'dr8'),
              ('sdss.json', 'dr9'),
              ('sdss.json', 'dr10'),
              ('sdss.json', 'dr11'),
              ('sdss.json', 'dr12'),
              ('desi.json', 'datachallenge'),
              ('desi.json', 'imaging'),
              ('desi.json', 'mocks'),
              ('desi.json', 'release'),
              ('desi.json', 'spectro'),
              ('desi.json', 'target')]


@pytest.mark.parametrize('filename,section', parameters)
def test_json(filename, section):
    """Check a generic JSON file for existence and required section.
    """
    assert resource_exists('hpsspy', f'data/{filename}'), f"Could not find {filename}!"
    t = resource_stream('hpsspy', f'data/{filename}')
    j = t.read()
    t.close()
    try:
        hpss_map = json.loads(j)
    except TypeError:
        hpss_map = json.loads(j.decode('utf8'))
    assert section in hpss_map, f"Section {section} is not in {filename}!"
