# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_os
~~~~~~~~~~~~~~~~~~~

Test the functions in the os subpackage.
"""
import pytest
from ..os._os import chmod, listdir, makedirs, mkdir, lstat, stat, walk
from ..os.path import isdir, isfile, islink
from .. import HpssOSError


class MockFile(object):
    """Simple mock object for use with testing walk().
    """
    def __init__(self, isdir, string):
        self.isdir = isdir
        self.string = string
        self.path = f'/path/{string}'
        self.st_size = 12345
        self.st_mtime = 54321

    def __str__(self):
        return self.string


@pytest.fixture
def mock_call():
    """Simple fixture to capture function calls.
    """

    class SaveArgs(object):
        """Save a function call's arguments for later inspection.
        """
        def __init__(self, return_values, raises=None):
            self.counter = 0
            self.return_values = return_values
            self.raises = raises
            self.args = list()
            self.kwargs = list()

        def __call__(self, *args, **kwargs):
            self.args.append(tuple(args))
            self.kwargs.append(kwargs)
            if self.raises:
                raise self.raises
            r = self.return_values[self.counter]
            self.counter += 1
            return r

    return SaveArgs


def test_chmod(monkeypatch, mock_call):
    """Test the chmod() function.
    """
    m = mock_call(['All good!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    chmod('/home/b/bweaver/foo.txt', 0o664)
    assert m.args[0] == ('chmod', '436', '/home/b/bweaver/foo.txt')


def test_chmod_error(monkeypatch, mock_call):
    """Test the chmod() throwing an error.
    """
    m = mock_call(['** Error!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        chmod('/home/b/bweaver/foo.txt', 0o664)
    assert err.value.args[0] == "** Error!"
    assert m.args[0] == ('chmod', '436', '/home/b/bweaver/foo.txt')


def test_listdir_error(monkeypatch, mock_call):
    """Test the listdir() function throwing an error.
    """
    m = mock_call(['** Error!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        files = listdir('/home/b/bweaver')
    assert err.value.args[0] == '** Error!'
    assert m.args[0] == ('ls', '-Da', '/home/b/bweaver')


def test_listdir_bad_line(monkeypatch, mock_call):
    """Test the listdir() function with bad data.
    """
    m = mock_call(['/home/b/bweaver:\nGarbage line'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        files = listdir('/home/b/bweaver')
    assert err.value.args[0] == "Could not match line!\nGarbage line"
    assert m.args[0] == ('ls', '-Da', '/home/b/bweaver')


def test_listdir(monkeypatch, mock_call):
    """Test the listdir() function.
    """
    foo = '''/home/b/bweaver:
-rw-rw----    1 bweaver   desi     29956061184 Thu May 15 07:44:21 2014 cosmos_nvo.tar
-rw-rw----    1 bweaver   desi           61184 Thu May 15 07:49:34 2014 cosmos_nvo.tar.idx
'''
    m = mock_call([foo])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    files = listdir('/home/b/bweaver')
    assert files[0].ishtar
    assert m.args[0] == ('ls', '-Da', '/home/b/bweaver')


def test_makedirs_error(monkeypatch, mock_call):
    """Test the makedirs() function throwing an error.
    """
    m = mock_call(['** Error!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        makedirs('/home/b/bweaver', '2775')
    assert err.value.args[0] == '** Error!'
    assert m.args[0] == ('mkdir', '-p', '-m', '2775', '/home/b/bweaver')


def test_makedirs_with_mode(monkeypatch, mock_call):
    """Test the makedirs() function setting the mode.
    """
    m = mock_call(['All good!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    makedirs('/home/b/bweaver', '2775')
    assert m.args[0] == ('mkdir', '-p', '-m', '2775', '/home/b/bweaver')


def test_makedirs(monkeypatch, mock_call):
    """Test the makedirs() function.
    """
    m = mock_call(['All good!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    makedirs('/home/b/bweaver')
    assert m.args[0] == ('mkdir', '-p', '/home/b/bweaver')


def test_mkdir_error(monkeypatch, mock_call):
    """Test the mkdir() function throwing an error.
    """
    m = mock_call(['** Error!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        mkdir('/home/b/bweaver', '2775')
    assert err.value.args[0] == '** Error!'
    assert m.args[0] == ('mkdir', '-m', '2775', '/home/b/bweaver')


def test_mkdir_with_mode(monkeypatch, mock_call):
    """Test the mkdir() function setting the mode.
    """
    m = mock_call(['All good!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    mkdir('/home/b/bweaver', '2775')
    assert m.args[0] == ('mkdir', '-m', '2775', '/home/b/bweaver')


def test_mkdir(monkeypatch, mock_call):
    """Test the makedirs() function.
    """
    m = mock_call(['All good!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    mkdir('/home/b/bweaver')
    assert m.args[0] == ('mkdir', '/home/b/bweaver')


def test_stat_error(monkeypatch, mock_call):
    """Test the stat() function throwing an error.
    """
    m = mock_call(['** Error!'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        s = stat("desi/cosmos_nvo.tar")
    assert err.value.args[0] == '** Error!'
    assert m.args[0] == ('ls', '-Dd', 'desi/cosmos_nvo.tar')


def test_stat_bad_line(monkeypatch, mock_call):
    """Test the stat() function with bad data.
    """
    m = mock_call(['Garbage line'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        s = stat("desi/cosmos_nvo.tar")
    assert err.value.args[0] == "Could not match line!\nGarbage line"
    assert m.args[0] == ('ls', '-Dd', 'desi/cosmos_nvo.tar')


def test_stat(monkeypatch, mock_call):
    """Test the stat() function.
    """
    m = mock_call(['desi:\n-rw-rw----    1 bweaver   desi     29956061184 Thu May 15 07:49:34 2014 cosmos_nvo.tar\n'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    s = stat("desi/cosmos_nvo.tar")
    assert s.st_size == 29956061184
    assert s.st_mode == 33200
    assert m.args[0] == ('ls', '-Dd', 'desi/cosmos_nvo.tar')


def test_stat_multiple_response(monkeypatch, mock_call):
    """Test the stat() function with multiple responses.

    This is a rare error condition.
    """
    foo = '''desi:
-rw-rw----    1 bweaver   desi     29956061184 Thu May 15 07:49:34 2014 cosmos_nvo.tar
desi:
-rw-rw----    1 bweaver   desi     29956061184 Thu May 15 07:49:34 2014 cosmos_nvo.tar.idx
'''
    m = mock_call([foo])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        s = stat("desi/cosmos_nvo.tar")
    assert err.value.args[0] == "Non-unique response for desi/cosmos_nvo.tar!"
    assert m.args[0] == ('ls', '-Dd', 'desi/cosmos_nvo.tar')


def test_stat_symlink(monkeypatch, mock_call):
    """Test the stat() function with a symlink.
    """
    m = mock_call(['lrwxrwxrwx    1 bweaver   bweaver           21 Fri Aug 22 11:32:09 2014 cosmo@ -> /nersc/projects/cosmo',
                  'drwxrws---    6 nugent    cosmo            512 Tue Jun  4 11:06:43 2019 cosmo'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    s = stat("cosmo")
    assert s.isdir
    assert m.args[0] == ('ls', '-Dd', 'cosmo')
    assert m.args[1] == ('ls', '-Dd', '/nersc/projects/cosmo')


def test_stat_different_symlink(monkeypatch, mock_call):
    """Test the stat() function with a different symlink.

    Original test had "This may be pointing to some unexpected behavior."
    Not sure what this means any longer.
    """
    m = mock_call(['lrwxrwxrwx    1 bweaver   bweaver           21 Fri Aug 22 11:32:09 2014 cosmo@ -> cosmo.old',
                  'drwxrws---    6 nugent    cosmo            512 Fri Aug 22 11:32:09 2014 cosmo.old'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    s = stat("cosmo")
    assert s.isdir
    assert m.args[0] == ('ls', '-Dd', 'cosmo')
    assert m.args[1] == ('ls', '-Dd', 'cosmo.old')


def test_lstat_is_link(monkeypatch, mock_call):
    """Test the lstat() function.
    """
    m = mock_call(['lrwxrwxrwx    1 bweaver   bweaver           21 Fri Aug 22 11:32:09 2014 cosmo@ -> /nersc/projects/cosmo\n',
                  'drwxrws---    6 nugent    cosmo            512 Tue Jun  4 11:06:43 2019 cosmo'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    s = lstat('cosmo')
    assert s.islink
    assert m.args[0] == ('ls', '-Dd', 'cosmo')
    # assert m.args[1] == ('ls', '-Dd', '/nersc/projects/cosmo')


def test_lstat_not_link(monkeypatch, mock_call):
    """Test the lstat() function for non-links.
    """
    m = mock_call(['drwxr-sr-x    3 bweaver   bweaver          512 Mon Oct  4 10:34:20 2010 test'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    s = lstat('test')
    assert not s.islink
    assert m.args[0] == ('ls', '-Dd', 'test')


def test_isdir(monkeypatch, mock_call):
    """Test the isdir() function.
    """
    m = mock_call(['drwxr-sr-x    3 bweaver   bweaver          512 Mon Oct  4 10:43:20 2010 test'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    assert isdir('test')
    assert m.args[0] == ('ls', '-Dd', 'test')


def test_isfile(monkeypatch, mock_call):
    """Test the isfile() function.
    """
    foo = '''desi:
-rw-rw----    1 bweaver   desi     29956061184 Thu May 15 12:34:56 2014 cosmos_nvo.tar
'''
    m = mock_call([foo])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    assert isfile('desi/cosmos_nvo.tar')
    assert m.args[0] == ('ls', '-Dd', 'desi/cosmos_nvo.tar')


def test_islink(monkeypatch, mock_call):
    """Test the islink() function.
    """
    m = mock_call(['lrwxrwxrwx    1 bweaver   bweaver           21 Fri Aug 22 01:23:45 2014 cosmo@ -> /nersc/projects/cosmo',
                  '/nersc/projects:\ndrwxrwxr-x    1 bweaver   bweaver           21 Fri Aug 22 01:23:45 2014 cosmo'])
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    assert islink('cosmo')
    assert m.args[0] == ('ls', '-Dd', 'cosmo')
    # assert m.args[1] == ('ls', '-Dd', '/nersc/projects/cosmo')


def test_walk_error(monkeypatch, mock_call):
    """Test the walk() function throwing an error.
    """
    r = HpssOSError('foobar')
    m = mock_call(['Error message'], raises=r)
    e = mock_call(['Return value'])
    monkeypatch.setattr('hpsspy.os._os.listdir', m)
    w = walk('/home/b/bweaver', onerror=e)
    try:
        n = next(w)
    except StopIteration:
        pass
    assert m.args[0] == ('/home/b/bweaver', )
    assert e.args[0] == (r, )


def test_walk(monkeypatch, mock_call):
    """Test the walk() function.
    """
    d = MockFile(True, 'subdir')
    f = MockFile(False, 'name')
    ld = mock_call([[d, f], []])
    i = mock_call([False])
    monkeypatch.setattr('hpsspy.os._os.listdir', ld)
    monkeypatch.setattr('hpsspy.os._os.islink', i)
    w = walk('/home/b/bweaver')
    n = next(w)
    assert n == ('/home/b/bweaver', [d], [f])
    assert ld.args[0] == ('/home/b/bweaver', )
    n = next(w)
    assert n == ('/home/b/bweaver/subdir', [], [])
    assert ld.args[1] == ('/home/b/bweaver/subdir', )
    assert i.args[0] == ('/home/b/bweaver/subdir', )


def test_walk_topdown(monkeypatch, mock_call):
    """Test the walk() function in topdown mode.
    """
    d = MockFile(True, 'subdir')
    f = MockFile(False, 'name')
    ld = mock_call([[d, f], []])
    i = mock_call([False])
    monkeypatch.setattr('hpsspy.os._os.listdir', ld)
    monkeypatch.setattr('hpsspy.os._os.islink', i)
    w = walk('/home/b/bweaver', topdown=False)
    n = next(w)
    assert n == ('/home/b/bweaver/subdir', [], [])
    assert i.args[0] == ('/home/b/bweaver/subdir', )
    n = next(w)
    assert n == ('/home/b/bweaver', [d], [f])
    assert ld.args[0] == ('/home/b/bweaver', )
    assert ld.args[1] == ('/home/b/bweaver/subdir', )
