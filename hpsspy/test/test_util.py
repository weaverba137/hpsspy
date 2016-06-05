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


class TestUtil(unittest.TestCase):
    """Test the functions in the util subpackage.
    """

    def setUp(self):
        self.PY3 = sys.version_info[0] > 2
        # Store the original value of env variables, if present.
        self.env = {'TMPDIR': None, 'HPSS_DIR': None}
        for e in self.env:
            if e in os.environ:
                self.env[e] = os.environ['TMPDIR']

    def tearDown(self):
        # Restore the original value of env variables, if they were present.
        for e in self.env:
            if self.env[e] is None:
                if e in os.environ:
                    del os.environ[e]
            else:
                os.environ[e] = self.env[e]

    def setup_bin(self, command):
        real_command = resource_filename('hpsspy.test', 't/'+command)
        hpss_dir = os.path.dirname(real_command)
        os.environ['HPSS_DIR'] = hpss_dir
        os.mkdir(os.path.join(hpss_dir, 'bin'))
        os.symlink(real_command, os.path.join(hpss_dir, 'bin', command))

    def remove_bin(self, command):
        hpss_dir = os.environ['HPSS_DIR']
        os.remove(os.path.join(hpss_dir, 'bin', command))
        os.rmdir(os.path.join(hpss_dir, 'bin'))

    def test_HpssFile(self):
        """Test the HpssFile object.
        """
        lspath = '/home/b/bweaver'
        names = ('boss', 'cosmo', 'desi', 'test')
        links = ('/nersc/projects/boss', '/nersc/projects/cosmo',
                 '/nersc/projects/desi', None)
        modes = (0777, 0777, 0777, 02755)
        mtimes = (datetime.datetime(2008, 4, 3, 0, 0, 0),
                  datetime.datetime(2014, 8, 22, 0, 0, 0),
                  datetime.datetime(2013, 12, 16, 0, 0, 0),
                  datetime.datetime(2016, 4, 4, 13, 14, 0))
        data = (('l', 'rwxrwxrwx', '1', 'bweaver', 'bweaver',
                 '20', 'Apr', '3', '2008', 'boss@ -> /nersc/projects/boss'),
                ('l', 'rwxrwxrwx', '1', 'bweaver', 'bweaver',
                 '21', 'Aug', '22', '2014', 'cosmo@ -> /nersc/projects/cosmo'),
                ('l', 'rwxrwxrwx', '1', 'bweaver', 'bweaver',
                 '20', 'Dec', '16', '2013', 'desi@ -> /nersc/projects/desi'),
                ('d', 'rwxr-sr-x', '3', 'bweaver', 'bweaver',
                 '512', 'Apr', '4', '13:14', 'test'))
        repr_template = ("HpssFile('{0}', '{1}', '{2}', '{3}', '{4}', " +
                         "'{5}', '{6}', '{7}', '{8}', '{9}', '{10}')")

        files = list()
        for d in data:
            files.append(HpssFile(lspath, *d))
        for i, f in enumerate(files):
            r_data = [lspath] + list(data[i])
            self.assertEqual(repr(f), repr_template.format(*r_data))
            self.assertEqual(str(f), f.name)
            self.assertEqual(f.name, names[i])
            self.assertEqual(f.path, os.path.join(lspath, f.name))
            # self.assertTrue(f.isdir)
            m = f.st_mode
            mt = f.st_mtime
            if f.islink:
                self.assertEqual(f.st_mode, modes[i] | stat.S_IFLNK)
                self.assertEqual(f.readlink, links[i])
            else:
                self.assertTrue(f.isdir)
                self.assertEqual(f.st_mode, modes[i] | stat.S_IFDIR)
                with self.assertRaises(HpssOSError):
                    r = f.readlink
            self.assertEqual(f.st_mtime, int(mtimes[i].strftime('%s')))

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
        self.setup_bin('hsi')
        os.environ['TMPDIR'] = os.environ['HPSS_DIR']
        pre_command = ['-O', os.path.join(os.environ['TMPDIR'], 'hsi.txt'),
                       '-s', 'archive']
        command = ['ls', '-l', 'foo']
        out = hsi(*command)
        self.assertEqual(out.strip(), ' '.join(pre_command + command))
        self.remove_bin('hsi')

    def test_htar(self):
        """Test passing arguments to the htar command.
        """
        self.setup_bin('htar')
        command = ['-cvf', 'foo/bar.tar', '-H', 'crc:verify=all', 'bar']
        out, err = htar(*command)
        if self.PY3:
            self.assertEqual(out.decode('utf8').strip(), ' '.join(command))
            self.assertEqual(err.decode('utf8').strip(), '')
        else:
            self.assertEqual(out.strip(), ' '.join(command))
            self.assertEqual(err.strip(), '')
        self.remove_bin('htar')

if __name__ == '__main__':
    unittest.main()
