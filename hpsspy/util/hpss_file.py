# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
#
from .. import HpssOSError
from ..os import stat as hpss_stat
from os.path import join
import stat
#
class hpss_file(object):
    """Contains lots of information about a file."""
    _file_modes = {'l':stat.S_IFLNK,'d':stat.S_IFDIR,'-':stat.S_IFREG}
    _months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    #
    #
    #
    def __init__(self,*args):
        """Usually this will be initialized by a tuple produced by listdir."""
        self.hpss_path = args[0]
        self.raw_permission = args[1]
        self.st_nlink = int(args[2])
        self.st_uid = args[3]
        self.st_gid = args[4]
        self.st_size = int(args[5])
        self.raw_month = args[6]
        self.raw_day = int(args[7])
        self.raw_year = args[8]
        self.raw_name = args[9]
        self.ishtar = False
        return
    #
    #
    #
    def __repr__(self):
        return str(self)
    #
    #
    #
    def __str__(self):
        return self.name
    #
    #
    #
    @property
    def islink(self):
        return self.raw_permission.startswith('l')
    #
    #
    #
    @property
    def isdir(self):
        if self.islink:
            new_path = self.readlink
            if new_path.startswith('/'):
                return hpss_stat(new_path).isdir
            else:
                return hpss_stat(join(self.hpss_path,new_path)).isdir
        else:
            return self.raw_permission.startswith('d')
    #
    #
    #
    @property
    def readlink(self):
        if self.islink:
            return self.raw_name.split('->')[1].strip()
        else:
            raise HpssOSError("Invalid argument: '{0}'".format(self.raw_name))
    #
    #
    #
    @property
    def name(self):
        if self.islink:
            return self.raw_name.split('->')[0].rstrip('@ ')
        else:
            return self.raw_name
    #
    #
    #
    @property
    def path(self):
        return join(self.hpss_path,self.name)
    #
    #
    #
    @property
    def st_mode(self):
        try:
            mode = self._file_modes[self.raw_permission[0]]
        except KeyError:
            raise
        if self.raw_permission[1] == 'r':
            mode |= stat.S_IRUSR
        if self.raw_permission[2] == 'w':
            mode |= stat.S_IWUSR
        if self.raw_permission[3] == 'x':
            mode |= stat.S_IXUSR
        if self.raw_permission[3] == 'S':
            mode |= stat.S_ISUID
        if self.raw_permission[3] == 's':
            mode |= (stat.S_IXUSR | stat.S_ISUID)
        if self.raw_permission[4] == 'r':
            mode |= stat.S_IRGRP
        if self.raw_permission[5] == 'w':
            mode |= stat.S_IWGRP
        if self.raw_permission[6] == 'x':
            mode |= stat.S_IXGRP
        if self.raw_permission[6] == 'S':
            mode |= stat.S_ISGID
        if self.raw_permission[6] == 's':
            mode |= (stat.S_IXGRP | stat.S_ISGID)
        if self.raw_permission[7] == 'r':
            mode |= stat.S_IROTH
        if self.raw_permission[8] == 'w':
            mode |= stat.S_IWOTH
        if self.raw_permission[9] == 'x':
            mode |= stat.S_IXOTH
        if self.raw_permission[9] == 'T':
            mode |= stat.S_ISVTX
        if self.raw_permission[9] == 't':
            mode |= (stat.S_IXOTH | stat.S_ISVTX)
        return mode
    #
    #
    #
    @property
    def st_mtime(self):
        from datetime import datetime
        seconds = 0
        month = self._months.index(self.raw_month) + 1
        if self.raw_year.find(':') > 0:
            hm = self.raw_year.split(':')
            hours = int(hm[0])
            minutes = int(hm[1])
            year = datetime.now().year
        else:
            hours = 0
            minutes = 0
            year = int(self.raw_year)
        return int(datetime(year, month, self.raw_day, hours, minutes, seconds).strftime('%s'))
