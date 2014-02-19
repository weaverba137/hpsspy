# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
#
from .. import HpssOSError
#
class hpss_file(object):
    """Contains lots of information about a file."""
    def __init__(self,*args):
        """Usually this will be initialized by a tuple produced by listdir."""
        self.raw_permission = args[0]
        self.st_nlink = int(args[1])
        self.st_uid = args[2]
        self.st_gid = args[3]
        self.st_size = int(args[4])
        self.raw_month = args[5]
        self.raw_day = int(args[6])
        self.raw_year = args[7]
        self.raw_name = args[8]
        return
    def __str__(self):
        if self.islink():
            return self.raw_name.split('->')[0].rstrip('@ ')
        else:
            return self.raw_name
    def islink(self):
        return self.raw_permission.startswith('l')
    def isdir(self):
        # TODO: This should also be true for links that point to directories.
        return self.raw_permission.startswith('d')
    def readlink(self):
        if islink(self):
            return self.raw_name.split('->')[1].strip()
        else:
            raise HpssOSError("Invalid argument: '{0}'".format(self.raw_name)
