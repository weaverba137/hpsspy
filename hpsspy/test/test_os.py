# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_os
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the os subpackage.
"""
import unittest
from unittest.mock import call, patch, MagicMock
# import json
# from pkg_resources import resource_filename
import os
import sys
from ..os._os import chmod, listdir, makedirs, mkdir, lstat, stat, walk
from ..os.path import isdir, isfile, islink
from .. import HpssOSError


class TestOs(unittest.TestCase):
    """Test the functions in the os subpackage.
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

    def test_chmod(self):
        """Test the chmod() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = '** Error!'
            with self.assertRaises(HpssOSError) as err:
                chmod('/home/b/bweaver/foo.txt', 0o664)
            self.assertEqual(str(err.exception), "** Error!")
            h.assert_called_with('chmod', '436', '/home/b/bweaver/foo.txt')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = 'All good!'
            chmod('/home/b/bweaver/foo.txt', 0o664)
            h.assert_called_with('chmod', '436', '/home/b/bweaver/foo.txt')

    def test_listdir(self):
        """Test the listdir() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = '** Error!'
            with self.assertRaises(HpssOSError) as err:
                files = listdir('/home/b/bweaver')
            self.assertEqual(str(err.exception), "** Error!")
            h.assert_called_with('ls', '-la', '/home/b/bweaver')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = '/home/b/bweaver:\nGarbage line'
            with self.assertRaises(HpssOSError) as err:
                files = listdir('/home/b/bweaver')
            self.assertEqual(str(err.exception),
                             "Could not match line!\nGarbage line")
            h.assert_called_with('ls', '-la', '/home/b/bweaver')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = ('/home/b/bweaver:\n'
                              '-rw-rw----    1 bweaver   desi     ' +
                              '29956061184 May 15  2014 cosmos_nvo.tar\n' +
                              '-rw-rw----    1 bweaver   desi     ' +
                              '      61184 May 15  2014 cosmos_nvo.tar.idx\n')
            files = listdir('/home/b/bweaver')
            h.assert_called_with('ls', '-la', '/home/b/bweaver')
            self.assertTrue(files[0].ishtar)

    def test_makedirs(self):
        """Test the makedirs() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = '** Error!'
            with self.assertRaises(HpssOSError) as err:
                makedirs('/home/b/bweaver', '2775')
            self.assertEqual(str(err.exception), "** Error!")
            h.assert_called_with('mkdir', '-p', '-m', '2775',
                                 '/home/b/bweaver')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = 'All good!'
            makedirs('/home/b/bweaver', '2775')
            h.assert_called_with('mkdir', '-p', '-m', '2775',
                                 '/home/b/bweaver')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = 'All good!'
            makedirs('/home/b/bweaver')
            h.assert_called_with('mkdir', '-p', '/home/b/bweaver')

    def test_mkdir(self):
        """Test the mkdir() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = '** Error!'
            with self.assertRaises(HpssOSError) as err:
                mkdir('/home/b/bweaver', '2775')
            self.assertEqual(str(err.exception), "** Error!")
            h.assert_called_with('mkdir', '-m', '2775', '/home/b/bweaver')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = 'All good!'
            mkdir('/home/b/bweaver', '2775')
            h.assert_called_with('mkdir', '-m', '2775', '/home/b/bweaver')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = 'All good!'
            mkdir('/home/b/bweaver')
            h.assert_called_with('mkdir', '/home/b/bweaver')

    def test_stat(self):
        """Test the stat() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = '** Error!'
            with self.assertRaises(HpssOSError) as err:
                s = stat("desi/cosmos_nvo.tar")
            self.assertEqual(str(err.exception), "** Error!")
            h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = 'Garbage line'
            with self.assertRaises(HpssOSError) as err:
                s = stat("desi/cosmos_nvo.tar")
            self.assertEqual(str(err.exception),
                             "Could not match line!\nGarbage line")
            h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = ('desi:\n-rw-rw----    1 bweaver   desi     ' +
                              '29956061184 May 15  2014 cosmos_nvo.tar\n')
            s = stat("desi/cosmos_nvo.tar")
            h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
            self.assertEqual(s.st_size, 29956061184)
            self.assertEqual(s.st_mode, 33200)
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = ('desi:\n-rw-rw----    1 bweaver   desi     ' +
                              '29956061184 May 15  2014 cosmos_nvo.tar\n' +
                              'desi:\n-rw-rw----    1 bweaver   desi     ' +
                              '29956061184 May 15  2014 cosmos_nvo.tar.idx\n')
            with self.assertRaises(HpssOSError) as err:
                s = stat("desi/cosmos_nvo.tar")
            self.assertEqual(str(err.exception),
                             "Non-unique response for desi/cosmos_nvo.tar!")
            h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')
        with patch('hpsspy.os._os.hsi') as h:
            h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver           ' +
                              '21 Aug 22  2014 cosmo@ -> ' +
                              '/nersc/projects/cosmo\n'),
                             ('drwxrws---    6 nugent    cosmo            ' +
                              '512 Dec 16  2016 cosmo')]
            s = stat("cosmo")
            self.assertTrue(s.isdir)
            h.assert_has_calls([call('ls', '-ld', 'cosmo'),
                                call('ls', '-ld', '/nersc/projects/cosmo')])
        #
        # This may be pointing to some unexpected behavior.
        #
        with patch('hpsspy.os._os.hsi') as h:
            h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver      ' +
                              '21 Aug 22  2014 cosmo@ -> ' +
                              'cosmo.old\n'),
                             ('drwxrws---    6 nugent    cosmo       ' +
                              '512 Dec 16  2016 cosmo.old')]
            s = stat("cosmo")
            self.assertTrue(s.isdir)
            h.assert_has_calls([call('ls', '-ld', 'cosmo'),
                                call('ls', '-ld', 'cosmo.old')])

    def test_lstat(self):
        """Test the lstat() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver           ' +
                              '21 Aug 22  2014 cosmo@ -> ' +
                              '/nersc/projects/cosmo\n'),
                             ('drwxrws---    6 nugent    cosmo            ' +
                              '512 Dec 16  2016 cosmo')]
            s = lstat("cosmo")
            self.assertTrue(s.islink)
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = ('drwxr-sr-x    3 bweaver   bweaver          ' +
                              '512 Oct  4  2010 test')
            s = lstat("test")
            self.assertFalse(s.islink)

    def test_isdir(self):
        """Test the isdir() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = ('drwxr-sr-x    3 bweaver   bweaver          ' +
                              '512 Oct  4  2010 test')
            self.assertTrue(isdir('test'))
            h.assert_called_with('ls', '-ld', 'test')

    def test_isfile(self):
        """Test the isfile() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.return_value = ('desi:\n-rw-rw----    1 bweaver   desi     ' +
                              '29956061184 May 15  2014 cosmos_nvo.tar\n')
            self.assertTrue(isfile('desi/cosmos_nvo.tar'))
            h.assert_called_with('ls', '-ld', 'desi/cosmos_nvo.tar')

    def test_islink(self):
        """Test the islink() function.
        """
        with patch('hpsspy.os._os.hsi') as h:
            h.side_effect = [('lrwxrwxrwx    1 bweaver   bweaver           ' +
                              '21 Aug 22  2014 cosmo@ -> ' +
                              '/nersc/projects/cosmo\n'),
                             ('/nersc/projects:\n' +
                              'drwxrwxr-x    1 bweaver   bweaver           ' +
                              '21 Aug 22  2014 cosmo')]
            self.assertTrue(islink('cosmo'))
            h.assert_has_calls([call('ls', '-ld', 'cosmo')])

    def test_walk(self):
        """Test the walk() function.
        """
        #
        # Test onerror
        #
        e = MagicMock()
        err = HpssOSError('foobar')
        with patch('hpsspy.os._os.listdir') as ld:
            ld.side_effect = err
            w = walk('/home/b/bweaver', onerror=e)
            try:
                n = next(w)
            except StopIteration:
                pass
            ld.assert_called_with('/home/b/bweaver')
        e.assert_called_with(err)
        #
        # Test standard operation
        #
        d = MagicMock()
        d.isdir = True
        d.__str__.return_value = 'subdir'
        f = MagicMock()
        f.isdir = False
        with patch('hpsspy.os._os.listdir') as ld:
            with patch('hpsspy.os.path.islink') as i:
                i.return_value = False
                ld.side_effect = [[d, f], []]
                w = walk('/home/b/bweaver')
                n = next(w)
                self.assertEqual(n, ('/home/b/bweaver', [d], [f]))
                ld.assert_called_with('/home/b/bweaver')
                n = next(w)
                self.assertEqual(n, ('/home/b/bweaver/subdir', [], []))
                i.assert_called_with('/home/b/bweaver/subdir')
        #
        # Test topdown operation
        #
        d = MagicMock()
        d.isdir = True
        d.__str__.return_value = 'subdir'
        f = MagicMock()
        f.isdir = False
        with patch('hpsspy.os._os.listdir') as ld:
            with patch('hpsspy.os.path.islink') as i:
                i.return_value = False
                ld.side_effect = [[d, f], []]
                w = walk('/home/b/bweaver', topdown=False)
                n = next(w)
                self.assertEqual(n, ('/home/b/bweaver/subdir', [], []))
                i.assert_called_with('/home/b/bweaver/subdir')
                n = next(w)
                self.assertEqual(n, ('/home/b/bweaver', [d], [f]))
                ld.assert_called_with('/home/b/bweaver/subdir')


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
