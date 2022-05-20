# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_util
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the util subpackage.
"""
import pytest
import os
import stat
from datetime import datetime
from .. import HpssOSError
from ..util import HpssFile, get_hpss_dir, get_tmpdir, hsi, htar
from .test_os import mock_call, MockFile


def test_HpssFile():
    """Test the HpssFile object.
    """
    lspath = '/home/b/bweaver'
    names = ('boss', 'cosmo', 'desi', 'test', 'README.rst',
             'backup.tar', 'backup.tar.idx')
    links = ('/nersc/projects/boss', '/nersc/projects/cosmo',
             '/nersc/projects/desi', True, False, False, False)
    modes = (511, 511, 511, 1517, 432, 432, 432)
    mtimes = (datetime(2008, 4, 3, 13, 4, 5, tzinfo=HpssFile._pacific),
              datetime(2014, 8, 22, 11, 32, 9, tzinfo=HpssFile._pacific),
              datetime(2013, 12, 16, 15, 12, 59, tzinfo=HpssFile._pacific),
              datetime(2022, 4, 4, 13, 14, 15, tzinfo=HpssFile._pacific),
              datetime(2021, 7, 3, 12, 34, 56, tzinfo=HpssFile._pacific),
              datetime(2016, 2, 2, 9, 2, 7, tzinfo=HpssFile._pacific),
              datetime(2016, 2, 2, 9, 2, 13, tzinfo=HpssFile._pacific))
    data = (('l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver', 20, 'Thu', 'Apr', 3, '13:04:05', 2008, 'boss@ -> /nersc/projects/boss'),
            ('l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver', 21, 'Fri', 'Aug', 22, '11:32:09', 2014, 'cosmo@ -> /nersc/projects/cosmo'),
            ('l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver', 20, 'Mon', 'Dec', 16, '15:12:59', 2013, 'desi@ -> /nersc/projects/desi'),
            ('d', 'rwxr-sr-x', 3, 'bweaver', 'bweaver', 512, 'Mon', 'Apr', 4, '13:14:15', 2022, 'test'),
            ('-', 'rw-rw----', 1, 'bweaver', 'bweaver', 100, 'Sat', 'Jul', 3, '12:34:56', 2021, 'README.rst'),
            ('-', 'rw-rw----', 1, 'bweaver', 'bweaver', 100000, 'Tue', 'Feb', 2, '09:02:07', 2016, 'backup.tar'),
            ('-', 'rw-rw----', 1, 'bweaver', 'bweaver', 1000, 'Tue', 'Feb', 2, '09:02:13', 2016, 'backup.tar.idx'))
    htar_data = [('-', 'rw-rw----', 'bweaver/bweaver', '50', '2016-02-02', '12:34', 'a.txt'),
                 ('-', 'rw-rw----', 'bweaver/bweaver', '50', '2016-02-02', '12:34', 'b.txt'),
                 ('-', 'rw-rw----', 'bweaver/bweaver', '50', '2016-02-02', '12:34', 'c.txt')]
    repr_template = ("HpssFile('{0}', '{1}', '{2}', {3:d}, '{4}', " +
                     "'{5}', {6:d}, '{7}', '{8}', {9:d}, '{10}', {11:d}, '{12}')")

    files = list()
    for d in data:
        f = HpssFile(lspath, *d)
        if f.name == 'backup.tar':
            f.ishtar = True
            f._contents = htar_data
        files.append(f)
    for i, f in enumerate(files):
        r_data = [lspath] + list(data[i])
        assert repr(f) == repr_template.format(*r_data)
        assert str(f) == f.name
        assert f.name == names[i]
        assert f.path == os.path.join(lspath, f.name)
        m = f.st_mode
        mt = f.st_mtime
        if f.islink:
            assert f.st_mode == (modes[i] | stat.S_IFLNK)
            assert f.readlink == links[i]
        else:
            assert f.isdir == links[i]
            if links[i]:
                assert f.st_mode == (modes[i] | stat.S_IFDIR)
            else:
                assert f.st_mode == (modes[i] | stat.S_IFREG)
            with pytest.raises(HpssOSError):
                r = f.readlink
            if f.ishtar:
                assert f.htar_contents() == htar_data
            else:
                assert f.htar_contents() is None
        assert f.st_mtime == int(mtimes[i].strftime('%s'))


def test_HpssFile_unusual_mode():
    """Test HpssFile with unusual file types.
    """
    lspath = '/home/b/bweaver'
    f = HpssFile(lspath, 's', 'rw-rw----', 1, 'bweaver', 'bweaver',
                 1000, 'Tue', 'Feb', 2, '09:02:07', 2016, 'fake.socket')
    with pytest.raises(AttributeError) as err:
        m = f.st_mode
    assert err.value.args[0] == "Unknown file type, s, for fake.socket!"


def test_HpssFile_htar_contents_basic():
    """Test retrieval of htar file contents.
    """
    lspath = '/home/b/bweaver'
    f = HpssFile(lspath, '-', 'rw-rw-r--', 1, 'bweaver', 'bweaver',
                 12345, 'Fri', 'Aug', 22, '11:32:09', 2014, 'bundle.tar')
    assert f.htar_contents() is None
    f.ishtar = True
    f._contents = ['foo.txt']
    assert f.htar_contents() == ['foo.txt']


def test_HpssFile_htar_contents(monkeypatch, mock_call):
    """Test parsing of realistic htar file contents.
    """
    lspath = '/home/b/bweaver'
    f = HpssFile(lspath, '-', 'rw-rw-r--', 1, 'bweaver', 'bweaver',
                 12345, 'Fri', 'Aug', 22, '11:32:09', 2014, 'bundle.tar')
    f.ishtar = True
    foo = '''HTAR: -rw-rw-r-- bweaver/bweaver 100 2012-07-03 12:00 foo.txt
HTAR: -rw-rw-r-- bweaver/bweaver 100 2012-07-03 12:00 bar.txt
'''
    m = mock_call([(foo, '')])
    monkeypatch.setattr('hpsspy.util.htar', m)
    assert f.htar_contents() == [('-', 'rw-rw-r--', 'bweaver', 'bweaver', '100', '2012', '07', '03', '12:00', 'foo.txt'),
                                 ('-', 'rw-rw-r--', 'bweaver', 'bweaver', '100', '2012', '07', '03', '12:00', 'bar.txt')]
    assert m.args[0] == ('-t', '-f', '/home/b/bweaver/bundle.tar')


def test_HpssFile_st_mode():
    """Test all st_mode combinations.
    """
    lspath = '/home/b/bweaver'
    f = HpssFile(lspath, 'd', 'rwxrwsrwt', 1, 'bweaver', 'bweaver',
                 1000, 'Tue', 'Feb', 2, '09:02:07', 2016, 'fake.dir')
    assert f.st_mode == 18431
    f = HpssFile(lspath, '-', 'rwSrw-rwT', 1, 'bweaver', 'bweaver',
                 1000, 'Tue', 'Feb', 2, '09:02:07', 2016, 'fake.file')
    assert f.st_mode == 35766
    f = HpssFile(lspath, '-', 'rwsrwSrwT', 1, 'bweaver', 'bweaver',
                 1000, 'Tue', 'Feb', 2, '09:02:07', 2016, 'fake.file')
    assert f.st_mode == 36854


def test_HpssFile_isdir(monkeypatch, mock_call):
    """Test the isdir property on symbolic links.
    """
    lspath = '/home/b/bweaver'
    m = MockFile(True, 'foo')
    s = mock_call([m])
    monkeypatch.setattr('hpsspy.os.stat', s)
    f = HpssFile(lspath, 'l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                 21, 'Fri', 'Aug', 22, '11:32:09', 2014, 'cosmo@ -> /nersc/projects/cosmo')
    assert f.islink
    assert f.isdir
    assert s.args[0] == ('/nersc/projects/cosmo', )


def test_HpssFile_isdir_file(monkeypatch, mock_call):
    """Test the isdir property on symbolic link pointing to a file.
    """
    lspath = '/home/b/bweaver'
    m = MockFile(False, 'foo')
    s = mock_call([m])
    monkeypatch.setattr('hpsspy.os.stat', s)
    f = HpssFile(lspath, 'l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                 21, 'Fri', 'Aug', 22, '11:32:09', 2014, 'cosmo@ -> cosmo.txt')
    assert f.islink
    assert not f.isdir
    assert s.args[0] == ('/home/b/bweaver/cosmo.txt', )


def test_get_hpss_dir(monkeypatch):
    """Test searching for the HPSS_DIR variable.
    """
    monkeypatch.setenv('HPSS_DIR', '/path/to/hpss')
    assert get_hpss_dir() == '/path/to/hpss/bin'


def test_get_tmpdir(monkeypatch):
    """Test the TMPDIR search function.
    """
    myTmpDir = '/my/own/personal/temporary/directory'
    assert get_tmpdir(tmpdir=myTmpDir) == myTmpDir
    monkeypatch.setenv('TMPDIR', '/Temporary/TMPDIR')
    assert get_tmpdir() == '/Temporary/TMPDIR'
    monkeypatch.delenv('TMPDIR')
    assert get_tmpdir() == '/tmp'


def test_hsi(monkeypatch, tmp_path, mock_call):
    """Test passing arguments to the hsi command.
    """
    m = mock_call([0])
    monkeypatch.setenv('TMPDIR', str(tmp_path))
    monkeypatch.setenv('HPSS_DIR', '/foo/bar')
    monkeypatch.setattr('hpsspy.util.call', m)
    txt = tmp_path / 'hsi.txt'
    with open(txt, 'w') as t:
        t.write('This is a test.')
    pre_command = ['-O', str(txt), '-s', 'archive']
    command = ['ls', '-l', 'foo']
    out = hsi(*command)
    assert out.strip() == 'This is a test.'
    assert m.args[0] == (['/foo/bar/bin/hsi'] + pre_command + command, )


def test_htar(monkeypatch, mock_call):
    """Test passing arguments to the htar command.
    """
    m = mock_call([0])
    monkeypatch.setenv('HPSS_DIR', '/foo/bar')
    monkeypatch.setattr('hpsspy.util.call', m)
    command = ['-cvf', 'foo/bar.tar', '-H', 'crc:verify=all', 'bar']
    out, err = htar(*command)
    assert (out, err) == ('', '')
    assert m.args[0] == (['/foo/bar/bin/htar'] + command, )
    assert 'stdout' in m.kwargs[0]
    assert 'stderr' in m.kwargs[0]
