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
from logging import DEBUG
from pkg_resources import resource_filename, resource_stream
from ..scan import (validate_configuration, compile_map, files_to_hpss,
                    find_missing, process_missing, extract_directory_name,
                    iterrsplit, scan_disk, scan_hpss, physical_disks, _options)
from .test_os import mock_call, MockFile


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


def test_options(monkeypatch):
    """Test command-line parsing.
    """
    monkeypatch.setattr('sys.argv', ['missing_from_hpss', '--test', '--verbose',
                                     'config', 'release'])
    options = _options()
    assert options.test
    assert options.verbose
    assert options.config == 'config'


def test_scan_hpss_cached(caplog):
    """Test scan_hpss() using an existing cache.
    """
    caplog.set_level(DEBUG)
    cache = resource_filename('hpsspy.test', 't/hpss_cache.csv')
    hpss_files = scan_hpss('/hpss/root', cache)
    assert hpss_files['foo'][0] == 1
    assert hpss_files['bar'][1] == 3
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == f"Found cache file {cache}."


def test_scan_hpss(monkeypatch, caplog, tmp_path, mock_call):
    """Test scan_hpss() using an existing cache.
    """
    d = MockFile(True, 'subdir')
    f = MockFile(False, 'name')
    ff = MockFile(False, 'subname')
    ld = mock_call([[d, f], [ff]])
    i = mock_call([False])
    monkeypatch.setattr('hpsspy.os._os.listdir', ld)
    monkeypatch.setattr('hpsspy.os._os.islink', i)
    caplog.set_level(DEBUG)
    cache = tmp_path / 'temp_hpss_cache.csv'
    # cache = resource_filename('hpsspy.test', 't/hpss_cache.csv')
    hpss_files = scan_hpss('/hpss/root', str(cache))
    # print(hpss_files)
    assert hpss_files['/path/name'][0] == 12345
    assert hpss_files['/path/subname'][1] == 54321
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == "No HPSS cache file, starting scan at /hpss/root."
    assert caplog.records[1].levelname == 'DEBUG'
    assert caplog.records[1].message == "Scanning HPSS directory /hpss/root."
    assert caplog.records[2].levelname == 'DEBUG'
    assert caplog.records[2].message == "Scanning HPSS directory /hpss/root/subdir."
    expected_csv = """Name,Size,Mtime
/path/name,12345,54321
/path/subname,12345,54321
"""
    with cache.open() as csv:
        data = csv.read()
    assert data == expected_csv
    assert ld.args[0] == ('/hpss/root', )
    assert ld.args[1] == ('/hpss/root/subdir', )
    assert i.args[0] == ('/hpss/root/subdir', )


def test_scan_disk_cached(monkeypatch, caplog, mock_call):
    """Test the scan_disk() function using an existing cache.
    """
    m = mock_call([True])
    monkeypatch.setattr('os.path.exists', m)
    caplog.set_level(DEBUG)
    assert scan_disk(['/foo', '/bar'], 'cache_file')
    assert m.args[0] == ('cache_file', )
    assert caplog.records[0].levelname == 'DEBUG'
    assert caplog.records[0].message == "Using existing file cache: cache_file"


def test_scan_disk(monkeypatch, caplog, tmp_path, mock_call):
    """Test the scan_disk() function.
    """
    f = MockFile(False, 'name')
    ff = MockFile(False, 'subname')
    m = mock_call([[('/foo', ['subdir'], ['name']),
                    ('/foo/subdir', [], ['subname'])],
                   [('/bar', ['subdir'], ['name']),
                    ('/bar/subdir', [], ['subname'])]])
    # i = mock_call([False, False, False, False])
    s = mock_call([f, f, ff, f, ff])
    monkeypatch.setattr('os.walk', m)
    # monkeypatch.setattr('os.path.islink', i)
    monkeypatch.setattr('os.stat', s)
    caplog.set_level(DEBUG)
    cache = tmp_path / 'cache_file.csv'
    foo = scan_disk(['/foo', '/bar'], str(cache), overwrite=True)
    assert foo
    assert m.args[0] == ('/foo', )
    assert m.args[1] == ('/bar', )
    assert s.args[0] == (str(cache), )
    assert s.args[1] == ('/foo/name', )
    assert s.args[2] == ('/foo/subdir/subname', )
    assert s.args[3] == ('/bar/name', )
    assert s.args[4] == ('/bar/subdir/subname', )
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == "No disk cache file, starting scan."
    assert caplog.records[1].levelname == 'DEBUG'
    assert caplog.records[1].message == "Starting os.walk at /foo."
    assert caplog.records[2].levelname == 'DEBUG'
    assert caplog.records[2].message == "Scanning disk directory /foo."
    assert caplog.records[3].levelname == 'DEBUG'
    assert caplog.records[3].message == "Scanning disk directory /foo/subdir."
    assert caplog.records[4].levelname == 'DEBUG'
    assert caplog.records[4].message == "Starting os.walk at /bar."
    assert caplog.records[5].levelname == 'DEBUG'
    assert caplog.records[5].message == "Scanning disk directory /bar."
    assert caplog.records[6].levelname == 'DEBUG'
    assert caplog.records[6].message == "Scanning disk directory /bar/subdir."
    expected_csv = """Name,Size,Mtime
name,12345,54321
subdir/subname,12345,54321
name,12345,54321
subdir/subname,12345,54321
"""
    with cache.open() as csv:
        data = csv.read()
    assert data == expected_csv


def test_scan_disk_exception(monkeypatch, caplog, tmp_path, mock_call):
    """Test the scan_disk() function, throwing an exception.
    """
    err = OSError(12345, 'foobar', 'foo.txt')
    f = MockFile(False, 'name')
    ff = MockFile(False, 'subname')
    m = mock_call([[('/foo', ['subdir'], ['name']),
                    ('/foo/subdir', [], ['subname'])],
                   [('/bar', ['subdir'], ['name']),
                    ('/bar/subdir', [], ['subname'])]], raises=err)
    # i = mock_call([False, False, False, False])
    s = mock_call([f, f, ff, f, ff])
    monkeypatch.setattr('os.walk', m)
    # monkeypatch.setattr('os.path.islink', i)
    monkeypatch.setattr('os.stat', s)
    caplog.set_level(DEBUG)
    cache = tmp_path / 'cache_file.csv'
    foo = scan_disk(['/foo', '/bar'], str(cache), overwrite=True)
    assert not foo
    assert caplog.records[0].levelname == 'INFO'
    assert caplog.records[0].message == "No disk cache file, starting scan."
    assert caplog.records[1].levelname == 'DEBUG'
    assert caplog.records[1].message == "Starting os.walk at /foo."
    assert caplog.records[2].levelname == 'ERROR'
    assert caplog.records[2].message == "Exception encountered while creating disk cache file!"
    assert caplog.records[3].levelname == 'ERROR'
    assert caplog.records[3].message == "foobar"


def test_process_missing(monkeypatch, caplog, mock_call):
    """Test conversion of missing files into HPSS commands.
    """
    missing_cache = resource_filename('hpsspy.test', 't/missing_cache.json')
    getcwd = mock_call(['/working/directory', '/working/directory'])
    chdir = mock_call([None, None])
    isdir = mock_call([True])
    htar = mock_call([('out', '')])
    hsi = mock_call(['OK'])
    monkeypatch.setenv('HPSS_DIR', '/usr/local')
    monkeypatch.setattr('os.getcwd', getcwd)
    monkeypatch.setattr('os.chdir', chdir)
    monkeypatch.setattr('os.path.isdir', isdir)
    monkeypatch.setattr('hpsspy.scan.htar', htar)
    monkeypatch.setattr('hpsspy.os._os.hsi', hsi)
    caplog.set_level(DEBUG)
    process_missing(missing_cache, '/disk/root', '/hpss/root')
    assert chdir.args[0] == ('/disk/root/', )
    assert isdir.args[0] == ('/disk/root/test_basic_htar', )
    assert htar.args[0] == ('-cvf', '/hpss/root/test_basic_htar.tar', '-H', 'crc:verify=all', 'test_basic_htar')
    assert caplog.records[0].levelname == 'DEBUG'
    assert caplog.records[0].message == f"Processing missing files from {missing_cache}."
    assert caplog.records[1].levelname == 'DEBUG'
    assert caplog.records[1].message == "os.chdir('/disk/root/')"
    assert caplog.records[2].levelname == 'DEBUG'
    assert caplog.records[2].message == "makedirs('/hpss/root/', mode='2770')"
    assert caplog.records[3].levelname == 'INFO'
    assert caplog.records[3].message == "htar('-cvf', '/hpss/root/test_basic_htar.tar', '-H', 'crc:verify=all', 'test_basic_htar')"
    assert caplog.records[4].levelname == 'DEBUG'
    assert caplog.records[4].message == 'out'
    assert caplog.records[5].levelname == 'DEBUG'
    assert caplog.records[5].message == "os.chdir('/working/directory')"
