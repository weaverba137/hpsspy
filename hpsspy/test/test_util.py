# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.test.test_util
~~~~~~~~~~~~~~~~~~~~~

Test the functions in the util subpackage.
"""
#
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
#
import unittest
# import json
from pkg_resources import resource_filename
import os
import sys
import stat
import datetime
from .. import HpssOSError
from ..util import HpssFile, get_hpss_dir, get_tmpdir, hsi, htar

mock_available = True
try:
    from unittest.mock import patch, MagicMock
except:
    mock_available = False

class MockHpss(unittest.TestCase):
    """Provide access to mock HPSS commands.
    """

    @classmethod
    def setUpClass(cls):
        cls.PY3 = sys.version_info[0] > 2

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # Store the original value of env variables, if present.
        self.env = {'TMPDIR': None, 'HPSS_DIR': None}
        for e in self.env:
            if e in os.environ:
                self.env[e] = os.environ[e]
        hsi = resource_filename('hpsspy.test', 'bin/hsi')
        os.environ['HPSS_DIR'] = os.path.dirname(os.path.dirname(hsi))

    def tearDown(self):
        # Restore the original value of env variables, if they were present.
        for e in self.env:
            if self.env[e] is None:
                if e in os.environ:
                    del os.environ[e]
            else:
                os.environ[e] = self.env[e]


class TestUtil(MockHpss):
    """Test the functions in the util subpackage.
    """

    def test_HpssFile(self):
        """Test the HpssFile object.
        """
        lspath = '/home/b/bweaver'
        names = ('boss', 'cosmo', 'desi', 'test', 'README.rst',
                 'backup.tar', 'backup.tar.idx')
        links = ('/nersc/projects/boss', '/nersc/projects/cosmo',
                 '/nersc/projects/desi', True, False, False, False)
        modes = (511, 511, 511, 1517, 432, 432, 432)
        this_year = datetime.datetime.now().year
        mtimes = (datetime.datetime(2008, 4, 3, 0, 0, 0),
                  datetime.datetime(2014, 8, 22, 0, 0, 0),
                  datetime.datetime(2013, 12, 16, 0, 0, 0),
                  datetime.datetime(this_year, 4, 4, 13, 14, 0),
                  datetime.datetime(this_year, 7, 3, 12, 34, 0),
                  datetime.datetime(2016, 2, 2, 0, 0, 0),
                  datetime.datetime(2016, 2, 2, 0, 0, 0))
        data = (('l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                 20, 'Apr', 3, '2008', 'boss@ -> /nersc/projects/boss'),
                ('l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                 21, 'Aug', 22, '2014', 'cosmo@ -> /nersc/projects/cosmo'),
                ('l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                 20, 'Dec', 16, '2013', 'desi@ -> /nersc/projects/desi'),
                ('d', 'rwxr-sr-x', 3, 'bweaver', 'bweaver',
                 512, 'Apr', 4, '13:14', 'test'),
                ('-', 'rw-rw----', 1, 'bweaver', 'bweaver',
                 100, 'Jul', 3, '12:34', 'README.rst'),
                ('-', 'rw-rw----', 1, 'bweaver', 'bweaver',
                 100000, 'Feb', 2, '2016', 'backup.tar'),
                ('-', 'rw-rw----', 1, 'bweaver', 'bweaver',
                 1000, 'Feb', 2, '2016', 'backup.tar.idx'))
        htar_data = [('-', 'rw-rw----', 'bweaver/bweaver', '50', '2016-02-02',
                     '12:34', 'a.txt'),
                     ('-', 'rw-rw----', 'bweaver/bweaver', '50', '2016-02-02',
                      '12:34', 'b.txt'),
                     ('-', 'rw-rw----', 'bweaver/bweaver', '50', '2016-02-02',
                      '12:34', 'c.txt')]
        repr_template = ("HpssFile('{0}', '{1}', '{2}', {3:d}, '{4}', " +
                         "'{5}', {6:d}, '{7}', {8:d}, '{9}', '{10}')")

        files = list()
        for d in data:
            f = HpssFile(lspath, *d)
            if f.name == 'backup.tar':
                f.ishtar = True
                f._contents = htar_data
            files.append(f)
        for i, f in enumerate(files):
            r_data = [lspath] + list(data[i])
            self.assertEqual(repr(f), repr_template.format(*r_data))
            self.assertEqual(str(f), f.name)
            self.assertEqual(f.name, names[i])
            self.assertEqual(f.path, os.path.join(lspath, f.name))
            m = f.st_mode
            mt = f.st_mtime
            if f.islink:
                self.assertEqual(f.st_mode, modes[i] | stat.S_IFLNK)
                self.assertEqual(f.readlink, links[i])
            else:
                self.assertEqual(f.isdir, links[i])
                if links[i]:
                    self.assertEqual(f.st_mode, modes[i] | stat.S_IFDIR)
                else:
                    self.assertEqual(f.st_mode, modes[i] | stat.S_IFREG)
                with self.assertRaises(HpssOSError):
                    r = f.readlink
                if f.ishtar:
                    self.assertListEqual(f.htar_contents(), htar_data)
                else:
                    self.assertIsNone(f.htar_contents())
            self.assertEqual(f.st_mtime, int(mtimes[i].strftime('%s')))
        #
        # Test funky modes.
        #
        f = HpssFile(lspath, 's', 'rw-rw----', 1, 'bweaver', 'bweaver',
                     1000, 'Feb', 2, '2016', 'fake.socket')
        with self.assertRaises(AttributeError) as err:
            m = f.st_mode
        self.assertEqual(str(err.exception),
                         "Unknown file type, s, for fake.socket!")

    @unittest.skipUnless(mock_available, "Skipping test that requires unittest.mock.")
    def test_HpssFile_isdir(self):
        """Test the isdir property on symbolic links.
        """
        lspath = '/home/b/bweaver'
        with patch('hpsspy.os.stat') as s:
            m = MagicMock()
            m.isdir = True
            s.return_value = m
            f = HpssFile(lspath, 'l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                         21, 'Aug', 22, '2014', 'cosmo@ -> /nersc/projects/cosmo')
            self.assertTrue(f.islink)
            self.assertTrue(f.isdir)
            s.assert_called_with('/nersc/projects/cosmo')
        with patch('hpsspy.os.stat') as s:
            m = MagicMock()
            m.isdir = False
            s.return_value = m
            f = HpssFile(lspath, 'l', 'rwxrwxrwx', 1, 'bweaver', 'bweaver',
                         21, 'Aug', 22, '2014', 'cosmo@ -> cosmo.txt')
            self.assertTrue(f.islink)
            self.assertFalse(f.isdir)
            s.assert_called_with('/home/b/bweaver/cosmo.txt')

    @unittest.skipUnless(mock_available, "Skipping test that requires unittest.mock.")
    def test_HpssFile_htar_contents(self):
        """Test retrieval of htar file contents.
        """
        lspath = '/home/b/bweaver'
        f = HpssFile(lspath, '-', 'rw-rw-r--', 1, 'bweaver', 'bweaver',
                     12345, 'Aug', 22, '2014', 'bundle.tar')
        self.assertIsNone(f.htar_contents())
        f.ishtar = True
        f._contents = ['foo.txt']
        self.assertListEqual(f.htar_contents(), ['foo.txt'])
        f._contents = None
        with patch('hpsspy.util.htar') as h:
            h.return_value = ('HTAR: -rw-rw-r-- bweaver/bweaver 100 2012-07-03 12:00 foo.txt\nHTAR: -rw-rw-r-- bweaver/bweaver 100 2012-07-03 12:00 bar.txt', '')
            self.assertListEqual(f.htar_contents(),
                                 [('-', 'rw-rw-r--', 'bweaver', 'bweaver', '100', '2012', '07', '03', '12:00', 'foo.txt'),
                                  ('-', 'rw-rw-r--', 'bweaver', 'bweaver', '100', '2012', '07', '03', '12:00', 'bar.txt')])
            h.assert_called_with('-t', '-f', '/home/b/bweaver/bundle.tar')

    def test_get_hpss_dir(self):
        """Test searching for the HPSS_DIR variable.
        """
        os.environ['HPSS_DIR'] = '/path/to/hpss'
        self.assertEqual(get_hpss_dir(), '/path/to/hpss/bin')

    def test_get_tmpdir(self):
        """Test the TMPDIR search function.
        """
        myTmpDir = '/my/own/personal/temporary/directory'
        self.assertEqual(get_tmpdir(tmpdir=myTmpDir), myTmpDir)
        if self.env['TMPDIR'] is None:
            os.environ['TMPDIR'] = '/Temporary/TMPDIR'
            self.assertEqual(get_tmpdir(), '/Temporary/TMPDIR')
        else:
            self.assertEqual(get_tmpdir(), self.env['TMPDIR'])
        del os.environ['TMPDIR']
        self.assertEqual(get_tmpdir(), '/tmp')

    def test_hsi(self):
        """Test passing arguments to the hsi command.
        """
        os.environ['TMPDIR'] = os.environ['HPSS_DIR']
        pre_command = ['-O', os.path.join(os.environ['TMPDIR'], 'hsi.txt'),
                       '-s', 'archive']
        command = ['ls', '-l', 'foo']
        out = hsi(*command)
        self.assertEqual(out.strip(), ' '.join(command))

    def test_htar(self):
        """Test passing arguments to the htar command.
        """
        command = ['-cvf', 'foo/bar.tar', '-H', 'crc:verify=all', 'bar']
        out, err = htar(*command)
        self.assertEqual(out.strip(), ' '.join(command))
        self.assertEqual(err.strip(), '')


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
