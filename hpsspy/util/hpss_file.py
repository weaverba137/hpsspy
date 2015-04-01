# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
#
from __future__ import absolute_import, division, print_function, unicode_literals
#
from hpsspy import HpssOSError
from hpsspy.os import stat as hpss_stat
from hpsspy.os import htarre
from .htar import htar
from os.path import join
import stat
#
class hpss_file(object):
    """This class is used to store and access an HPSS file's metadata.

    Attributes
    ----------
    hpss_path : str
        Path on the HPSS filesystem.
    raw_type : str
        Raw type string.
    raw_permission : str
        Raw permission string.
    st_nlink : int
        Number of hard links.
    st_uid : str
        Owner's name.
    st_gid : str
        Group name.
    st_size : int
        File size in bytes.
    raw_month : str
        Month of modification time.
    raw_day : int
        Day of modification time.
    raw_year : str
        Year of modification time.
    raw_name : str
        Name of file.
    ishtar : bool
        ``True`` if the file is an htar file.
    """
    _file_modes = {'l':stat.S_IFLNK,'d':stat.S_IFDIR,'-':stat.S_IFREG}
    _months = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec')
    #
    #
    #
    def __init__(self,*args):
        """Usually this will be initialized by a tuple produced by listdir."""
        self.hpss_path = args[0]
        self.raw_type = args[1]
        self.raw_permission = args[2]
        self.st_nlink = int(args[3])
        self.st_uid = args[4]
        self.st_gid = args[5]
        self.st_size = int(args[6])
        self.raw_month = args[7]
        self.raw_day = int(args[8])
        self.raw_year = args[9]
        self.raw_name = args[10]
        self.ishtar = False
        self._contents = None # placeholder for htar file contents.
        self._property_cache = dict()
        return
    #
    #
    #
    def __repr__(self):
        return "hpss_file('{0}','{1}','{2}','{3:d}','{4}','{5}','{6:d}','{7}','{8:d}','{9}','{10}')".format(
            self.hpss_path,
            self.raw_type,
            self.raw_permission,
            self.st_nlink,
            self.st_uid,
            self.st_gid,
            self.st_size,
            self.raw_month,
            self.raw_day,
            self.raw_year,
            self.raw_name)
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
        return self.raw_type == 'l'
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
            return self.raw_type == 'd'
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
        if 'st_mode' in self._property_cache:
            return self._property_cache['st_mode']
        else:
            try:
                mode = self._file_modes[self.raw_type]
            except KeyError:
                raise
            if self.raw_permission[0] == 'r':
                mode |= stat.S_IRUSR
            if self.raw_permission[1] == 'w':
                mode |= stat.S_IWUSR
            if self.raw_permission[2] == 'x':
                mode |= stat.S_IXUSR
            if self.raw_permission[2] == 'S':
                mode |= stat.S_ISUID
            if self.raw_permission[2] == 's':
                mode |= (stat.S_IXUSR | stat.S_ISUID)
            if self.raw_permission[3] == 'r':
                mode |= stat.S_IRGRP
            if self.raw_permission[4] == 'w':
                mode |= stat.S_IWGRP
            if self.raw_permission[5] == 'x':
                mode |= stat.S_IXGRP
            if self.raw_permission[5] == 'S':
                mode |= stat.S_ISGID
            if self.raw_permission[5] == 's':
                mode |= (stat.S_IXGRP | stat.S_ISGID)
            if self.raw_permission[6] == 'r':
                mode |= stat.S_IROTH
            if self.raw_permission[7] == 'w':
                mode |= stat.S_IWOTH
            if self.raw_permission[8] == 'x':
                mode |= stat.S_IXOTH
            if self.raw_permission[8] == 'T':
                mode |= stat.S_ISVTX
            if self.raw_permission[8] == 't':
                mode |= (stat.S_IXOTH | stat.S_ISVTX)
            self._property_cache['st_mode'] = mode
            return mode
    #
    #
    #
    @property
    def st_mtime(self):
        from datetime import datetime
        if 'st_mtime' in self._property_cache:
            return self._property_cache['st_mtime']
        else:
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
            mtime = int(datetime(year, month, self.raw_day, hours, minutes, seconds).strftime('%s'))
            self._property_cache['st_mtime'] = mtime
            return mtime
    #
    #
    #
    def htar_contents(self):
        """Return (and cache) the contents of an htar file."""
        if self.ishtar:
            if self._contents is None:
                out,err = htar('-t','-f',self.path)
                self._contents = list()
                for line in out.split('\n'):
                    m = htarre.match(line)
                    if m is not None:
                        self._contents.append(m.groups())
            return self._contents
        else:
            return None
