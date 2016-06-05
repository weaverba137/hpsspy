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
from ..util import get_hpss_dir, get_tmpdir, hsi, htar


class TestUtil(unittest.TestCase):
    """Test the functions in the util subpackage.
    """

    def setUp(self):
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
        # self.assertEqual(out.strip(), ' '.join(command))
        # self.assertEqual(err.strip(), '')
        self.remove_bin('htar')

if __name__ == '__main__':
    unittest.main()
