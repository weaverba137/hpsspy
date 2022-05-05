# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_scan
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the scan subpackage.
"""
import pytest
import json
import re
from pkg_resources import resource_filename, resource_stream
from ..scan import (compile_map, files_to_hpss, physical_disks,
                    validate_configuration, process_missing, iterrsplit,
                    extract_directory_name)


@pytest.fixture
def test_config():
    """Provide access to configuration file.
    """
    class TestConfig(object):
        """Simple class to set config_file attributes.
        """
        def __init__(self):
            self.config_name = resource_filename('hpsspy.test', 't/test_scan.json')
            config_file = resource_stream('hpsspy.test', 't/test_scan.json')
            self.config = json.loads(config_file.read().decode())
            config_file.close()

    return TestConfig()


def test_iterrsplit():
    """Test reverse re-joining a string.
    """
    results = ['d', 'c_d', 'b_c_d', 'a_b_c_d']
    for i, s in enumerate(iterrsplit('a_b_c_d', '_')):
        assert s == results[i]


def test_compile_map(test_config):
    """Test compiling regular expressions in the JSON configuration file.
    """
    new_map = compile_map(test_config.config, 'data')
    assert new_map['__exclude__'] == frozenset(['README.html'])
    for conf in test_config.config['data']:
        if conf != '__exclude__':
            for nm in new_map[conf]:
                assert nm[0].pattern in test_config.config['data'][conf]
                assert nm[1] == test_config.config['data'][conf][nm[0].pattern]
    #
    # Catch bad compiles
    #
    test_config.config['redux']['d1'] = {'d1/(r\\d{5,4})/.*$': 'd1/d1_\\1.tar'}
    with pytest.raises(re.error) as err:
        new_map = compile_map(test_config.config, 'redux')
    assert err.value.colno == 9


def test_files_to_hpss(test_config):
    """Test conversion of JSON files to directory dictionary.
    """
    hpss_map, config = files_to_hpss(test_config.config_name, 'data')
    assert config['root'] == '/temporary'
    for key in hpss_map['d2']:
        assert key[0].pattern in test_config.config['data']['d2']
        assert key[1] == test_config.config['data']['d2'][key[0].pattern]
    hpss_map, config = files_to_hpss('desi.json', 'datachallenge')
    desi_map = {"dc2/batch/.*$": "dc2/batch.tar",
                "dc2/([^/]+\\.txt)$": "dc2/\\1",
                "dc2/templates/[^/]+$": "dc2/templates/templates_files.tar"
                }
    for key in hpss_map['dc2']:
        assert key[0].pattern in desi_map
        assert key[1] == desi_map[key[0].pattern]
    hpss_map, config = files_to_hpss('foo.json', 'dr8')
    assert 'casload' in hpss_map


def test_physical_disks():
    """Test physical disk path setup.
    """
    release_root = '/foo/bar/baz/data'
    config = {'root': '/foo/bar/baz'}
    pd = physical_disks(release_root, config)
    assert pd == (release_root,)
    config['physical_disks'] = None
    pd = physical_disks(release_root, config)
    assert pd == (release_root,)
    config['physical_disks'] = False
    pd = physical_disks(release_root, config)
    assert pd == (release_root,)
    config['physical_disks'] = []
    pd = physical_disks(release_root, config)
    assert pd == (release_root,)
    config['physical_disks'] = ['baz']
    pd = physical_disks(release_root, config)
    assert pd == (release_root,)
    config['physical_disks'] = ['baz0', 'baz1', 'baz2']
    pd = physical_disks(release_root, config)
    assert pd == ('/foo/bar/baz0/data',
                  '/foo/bar/baz1/data',
                  '/foo/bar/baz2/data')
    config['physical_disks'] = ['/foo/bar0/baz',
                                '/foo/bar1/baz',
                                '/foo/bar2/baz']
    pd = physical_disks(release_root, config)
    assert pd == ('/foo/bar0/baz/data',
                  '/foo/bar1/baz/data',
                  '/foo/bar2/baz/data')


def test_validate_configuration_no_file(caplog):
    """Test the configuration file validator with a missing file.
    """
    status = validate_configuration('foo.bar')
    assert status == 1
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].message == "foo.bar might not be a JSON file!"
    assert caplog.records[1].levelname == 'CRITICAL'
    assert caplog.records[1].message == "foo.bar does not exist. Try again."


def test_validate_configuration_invalid_file(caplog):
    """Test the configuration file validator with an invalid file.
    """
    invalid = resource_filename('hpsspy.test', 't/invalid_file')
    status = validate_configuration(invalid)
    assert status == 1
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].message == f"{invalid} might not be a JSON file!"
    assert caplog.records[1].levelname == 'CRITICAL'
    assert caplog.records[1].message == f"{invalid} is not valid JSON."


def test_validate_configuration_valid_file(caplog, test_config):
    """Test the configuration file validator with a valid file.
    """
    status = validate_configuration(test_config.config_name)
    assert status == 0


def test_validate_configuration_partial_valid_file(caplog, tmp_path, test_config):
    """Test the configuration file validator with a valid file but missing some pieces.
    """
    c = test_config.config.copy()
    del c['__config__']
    tmp = tmp_path / 'missing_config.json'
    with tmp.open('w') as fd:
        json.dump(c, fd)
    status = validate_configuration(str(tmp))
    assert status == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == f"{tmp} does not contain a '__config__' section."


def test_validate_configuration_another_partial_valid_file(caplog, tmp_path, test_config):
    """Test the configuration file validator with a valid file but missing some other pieces.
    """
    c = test_config.config.copy()
    del c['__config__']['physical_disks']
    tmp = tmp_path / 'missing_physical.json'
    with tmp.open('w') as fd:
        json.dump(c, fd)
    status = validate_configuration(str(tmp))
    assert status == 0
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].message == f"{tmp} '__config__' section does not contain an entry for 'physical_disks'."


def test_validate_configuration_yet_another_partial_valid_file(caplog, tmp_path, test_config):
    """Test the configuration file validator with a valid file but missing some other pieces.
    """
    c = test_config.config.copy()
    del c['redux']['__exclude__']
    tmp = tmp_path / 'missing_exclude.json'
    with tmp.open('w') as fd:
        json.dump(c, fd)
    status = validate_configuration(str(tmp))
    assert status == 0
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].message == "Section 'redux' should at least have an '__exclude__' entry."


def test_validate_configuration_bad_regex(caplog, tmp_path, test_config):
    """Test the configuration file validator with an invalid regular expression.
    """
    c = test_config.config.copy()
    c['redux']['d1'] = {'d1/(r\\d{5,4})/.*$': 'd1/d1_\\1.tar'}
    tmp = tmp_path / 'bad_regex.json'
    with tmp.open('w') as fd:
        json.dump(c, fd)
    status = validate_configuration(str(tmp))
    assert status == 1
    assert caplog.records[0].levelname == 'CRITICAL'
    assert caplog.records[0].message == "Regular Expression error detected in section 'redux'!"


def test_process_missing():
    """Test conversion of missing files into HPSS commands.
    """
    pass


def test_extract_directory_name():
    """Test conversion of HTAR file name back into directory name.
    """
    d = extract_directory_name(('images/fpc_analysis/' +
                                'protodesi_images_fpc_analysis_' +
                                'stability_dither-33022.tar'))
    assert d == 'stability_dither-33022'
    d = extract_directory_name(('buzzard/buzzard_v1.6_desicut/8/' +
                                'buzzard_v1.6_desicut_8_7.tar'))
    assert d == '7'
    d = extract_directory_name('foo/bar/batch.tar')
    assert d == 'batch'
    d = extract_directory_name('batch.tar')
    assert d == 'batch'
