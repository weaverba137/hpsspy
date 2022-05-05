# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_os
~~~~~~~~~~~~~~~~~~~

Test the functions in the os subpackage.
"""
import pytest
# import unittest
# from unittest.mock import call, patch, MagicMock
# import json
# from pkg_resources import resource_filename
# import os
# import sys
from ..os._os import chmod, listdir, makedirs, mkdir, lstat, stat, walk
from ..os.path import isdir, isfile, islink
from .. import HpssOSError


class SaveArgs(object):
    """Save a function call's arguments for later inspection.
    """
    def __init__(self, return_value):
        self.return_value = return_value

    def __call__(self, *args):
        self.args = list(args)
        return self.return_value


@pytest.fixture
def mock_hsi():
    return SaveArgs


def test_chmod(monkeypatch, mock_hsi):
    """Test the chmod() function.
    """
    m = mock_hsi('All good!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    chmod('/home/b/bweaver/foo.txt', 0o664)
    assert m.args == ['chmod', '436', '/home/b/bweaver/foo.txt']


def test_chmod_error(monkeypatch, mock_hsi):
    """Test the chmod() throwing an error.
    """
    m = mock_hsi('** Error!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        chmod('/home/b/bweaver/foo.txt', 0o664)
    assert err.value.args[0] == "** Error!"
    assert m.args == ['chmod', '436', '/home/b/bweaver/foo.txt']


def test_listdir_error(monkeypatch, mock_hsi):
    """Test the listdir() function throwing an error.
    """
    m = mock_hsi('** Error!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        files = listdir('/home/b/bweaver')
    assert err.value.args[0] == '** Error!'
    assert m.args == ['ls', '-la', '/home/b/bweaver']


def test_listdir_bad_line(monkeypatch, mock_hsi):
    """Test the listdir() function with bad data.
    """
    m = mock_hsi('/home/b/bweaver:\nGarbage line')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        files = listdir('/home/b/bweaver')
    assert err.value.args[0] == "Could not match line!\nGarbage line"
    assert m.args == ['ls', '-la', '/home/b/bweaver']


def test_listdir(monkeypatch, mock_hsi):
    """Test the listdir() function.
    """
    foo = '''/home/b/bweaver:
-rw-rw----    1 bweaver   desi     29956061184 May 15  2014 cosmos_nvo.tar
-rw-rw----    1 bweaver   desi           61184 May 15  2014 cosmos_nvo.tar.idx
'''
    m = mock_hsi(foo)
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    files = listdir('/home/b/bweaver')
    assert files[0].ishtar
    assert m.args == ['ls', '-la', '/home/b/bweaver']


def test_makedirs_error(monkeypatch, mock_hsi):
    """Test the makedirs() function throwing an error.
    """
    m = mock_hsi('** Error!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        makedirs('/home/b/bweaver', '2775')
    assert err.value.args[0] == '** Error!'
    assert m.args == ['mkdir', '-p', '-m', '2775', '/home/b/bweaver']


def test_makedirs_with_mode(monkeypatch, mock_hsi):
    """Test the makedirs() function setting the mode.
    """
    m = mock_hsi('All good!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    makedirs('/home/b/bweaver', '2775')
    assert m.args == ['mkdir', '-p', '-m', '2775', '/home/b/bweaver']


def test_makedirs(monkeypatch, mock_hsi):
    """Test the makedirs() function.
    """
    m = mock_hsi('All good!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    makedirs('/home/b/bweaver')
    assert m.args == ['mkdir', '-p', '/home/b/bweaver']


def test_mkdir_error(monkeypatch, mock_hsi):
    """Test the mkdir() function throwing an error.
    """
    m = mock_hsi('** Error!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    with pytest.raises(HpssOSError) as err:
        mkdir('/home/b/bweaver', '2775')
    assert err.value.args[0] == '** Error!'
    assert m.args == ['mkdir', '-m', '2775', '/home/b/bweaver']


def test_mkdir_with_mode(monkeypatch, mock_hsi):
    """Test the mkdir() function setting the mode.
    """
    m = mock_hsi('All good!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    mkdir('/home/b/bweaver', '2775')
    assert m.args == ['mkdir', '-m', '2775', '/home/b/bweaver']


def test_mkdir(monkeypatch, mock_hsi):
    """Test the makedirs() function.
    """
    m = mock_hsi('All good!')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    mkdir('/home/b/bweaver')
    assert m.args == ['mkdir', '/home/b/bweaver']


# def test_stat(self):
#     """Test the stat() function.
#     """
#     with patch('hpsspy.os._os.hsi') as h:
#         h.return_value = '** Error!'
#         with self.assertRaises(HpssOSError) as err:
#             s = stat("desi/cosmos_nvo.tar")
#         self.assertEqual(str(err.exception), "** Error!")
#         h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
#     with patch('hpsspy.os._os.hsi') as h:
#         h.return_value = 'Garbage line'
#         with self.assertRaises(HpssOSError) as err:
#             s = stat("desi/cosmos_nvo.tar")
#         self.assertEqual(str(err.exception),
#                          "Could not match line!\nGarbage line")
#         h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
#     with patch('hpsspy.os._os.hsi') as h:
#         h.return_value = ('desi:\n-rw-rw----    1 bweaver   desi     ' +
#                           '29956061184 May 15  2014 cosmos_nvo.tar\n')
#         s = stat("desi/cosmos_nvo.tar")
#         h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
#         self.assertEqual(s.st_size, 29956061184)
#         self.assertEqual(s.st_mode, 33200)
#     with patch('hpsspy.os._os.hsi') as h:
#         h.return_value = ('desi:\n-rw-rw----    1 bweaver   desi     ' +
#                           '29956061184 May 15  2014 cosmos_nvo.tar\n' +
#                           'desi:\n-rw-rw----    1 bweaver   desi     ' +
#                           '29956061184 May 15  2014 cosmos_nvo.tar.idx\n')
#         with self.assertRaises(HpssOSError) as err:
#             s = stat("desi/cosmos_nvo.tar")
#         self.assertEqual(str(err.exception),
#                          "Non-unique response for desi/cosmos_nvo.tar!")
#         h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
#     with patch('hpsspy.os._os.hsi') as h:
#         h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver           ' +
#                           '21 Aug 22  2014 cosmo@ -> ' +
#                           '/nersc/projects/cosmo\n'),
#                          ('drwxrws---    6 nugent    cosmo            ' +
#                           '512 Dec 16  2016 cosmo')]
#         s = stat("cosmo")
#         self.assertTrue(s.isdir)
#         h.assert_has_calls([call('ls', '-ld', 'cosmo'),
#                             call('ls', '-ld', '/nersc/projects/cosmo')])
#     #
#     # This may be pointing to some unexpected behavior.
#     #
#     with patch('hpsspy.os._os.hsi') as h:
#         h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver      ' +
#                           '21 Aug 22  2014 cosmo@ -> ' +
#                           'cosmo.old\n'),
#                          ('drwxrws---    6 nugent    cosmo       ' +
#                           '512 Dec 16  2016 cosmo.old')]
#         s = stat("cosmo")
#         self.assertTrue(s.isdir)
#         h.assert_has_calls([call('ls', '-ld', 'cosmo'),
#                             call('ls', '-ld', 'cosmo.old')])
#
# def test_lstat(self):
#     """Test the lstat() function.
#     """
#     with patch('hpsspy.os._os.hsi') as h:
#         h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver           ' +
#                           '21 Aug 22  2014 cosmo@ -> ' +
#                           '/nersc/projects/cosmo\n'),
#                          ('drwxrws---    6 nugent    cosmo            ' +
#                           '512 Dec 16  2016 cosmo')]
#         s = lstat("cosmo")
#         self.assertTrue(s.islink)
#     with patch('hpsspy.os._os.hsi') as h:
#         h.return_value = ('drwxr-sr-x    3 bweaver   bweaver          ' +
#                           '512 Oct  4  2010 test')
#         s = lstat("test")
#         self.assertFalse(s.islink)


def test_isdir(monkeypatch, mock_hsi):
    """Test the isdir() function.
    """
    m = mock_hsi('drwxr-sr-x    3 bweaver   bweaver          512 Oct  4  2010 test')
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    assert isdir('test')
    assert m.args == ['ls', '-ld', 'test']


def test_isfile(monkeypatch, mock_hsi):
    """Test the isfile() function.
    """
    foo = '''desi:
-rw-rw----    1 bweaver   desi     29956061184 May 15  2014 cosmos_nvo.tar
'''
    m = mock_hsi(foo)
    monkeypatch.setattr('hpsspy.os._os.hsi', m)
    assert isfile('desi/cosmos_nvo.tar')
    assert m.args == ['ls', '-ld', 'desi/cosmos_nvo.tar']


# def test_islink(self):
#     """Test the islink() function.
#     """
#     with patch('hpsspy.os._os.hsi') as h:
#         h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver           ' +
#                           '21 Aug 22  2014 cosmo@ -> ' +
#                           '/nersc/projects/cosmo\n'),
#                          ('/nersc/projects:\n' +
#                           'drwxrwxr-x    1 bweaver   bweaver           ' +
#                           '21 Aug 22  2014 cosmo')]
#         self.assertTrue(islink('cosmo'))
#         h.assert_has_calls([call('ls', '-ld', 'cosmo')])
#
# def test_walk(self):
#     """Test the walk() function.
#     """
#     #
#     # Test onerror
#     #
#     e = MagicMock()
#     err = HpssOSError('foobar')
#     with patch('hpsspy.os._os.listdir') as ld:
#         ld.side_effect = err
#         w = walk('/home/b/bweaver', onerror=e)
#         try:
#             n = next(w)
#         except StopIteration:
#             pass
#         ld.assert_called_with('/home/b/bweaver')
#     e.assert_called_with(err)
#     #
#     # Test standard operation
#     #
#     d = MagicMock()
#     d.isdir = True
#     d.__str__.return_value = 'subdir'
#     f = MagicMock()
#     f.isdir = False
#     with patch('hpsspy.os._os.listdir') as ld:
#         with patch('hpsspy.os.path.islink') as i:
#             i.return_value = False
#             ld.side_effect = [[d, f], []]
#             w = walk('/home/b/bweaver')
#             n = next(w)
#             self.assertEqual(n, ('/home/b/bweaver', [d], [f]))
#             ld.assert_called_with('/home/b/bweaver')
#             n = next(w)
#             self.assertEqual(n, ('/home/b/bweaver/subdir', [], []))
#             i.assert_called_with('/home/b/bweaver/subdir')
#     #
#     # Test topdown operation
#     #
#     d = MagicMock()
#     d.isdir = True
#     d.__str__.return_value = 'subdir'
#     f = MagicMock()
#     f.isdir = False
#     with patch('hpsspy.os._os.listdir') as ld:
#         with patch('hpsspy.os.path.islink') as i:
#             i.return_value = False
#             ld.side_effect = [[d, f], []]
#             w = walk('/home/b/bweaver', topdown=False)
#             n = next(w)
#             self.assertEqual(n, ('/home/b/bweaver/subdir', [], []))
#             i.assert_called_with('/home/b/bweaver/subdir')
#             n = next(w)
#             self.assertEqual(n, ('/home/b/bweaver', [d], [f]))
#             ld.assert_called_with('/home/b/bweaver/subdir')
