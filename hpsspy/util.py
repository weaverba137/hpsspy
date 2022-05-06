# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
hpsspy.util
~~~~~~~~~~~

Low-level utilities.
"""
import os
import stat
import re
from datetime import datetime
from subprocess import call
from tempfile import TemporaryFile
import pytz
from . import HpssOSError


class HpssFile(object):
    """This class is used to store and access an HPSS file's metadata.

    Parameters
    ----------
    args : iterable
        This object this will normally be initialized by a tuple produced by
        :func:`hpsspy.os.listdir`.

    Attributes
    ----------
    hpss_path : :class:`str`
        Path on the HPSS filesystem.
    raw_type : :class:`str`
        Raw type string.
    raw_permission : :class:`str`
        Raw permission string.
    st_nlink : :class:`int`
        Number of hard links.
    st_uid : :class:`str`
        Owner's name.
    st_gid : :class:`str`
        Group name.
    st_size : :class:`int`
        File size in bytes.
    raw_dow : :class:`str`
        Day-of-week of modification time.
    raw_month : :class:`str`
        Month of modification time.
    raw_day : :class:`int`
        Day of modification time.
    raw_hms : :class:`str`
        H:M:S of modification time.
    raw_year : :class:`int`
        Year of modification time.
    raw_name : :class:`str`
        Name of file.
    ishtar : :class:`bool`
        ``True`` if the file is an htar file.
    """
    _htarre = re.compile(r"""HTAR:\s([dl-])        # file type
                             ([rwxsStT-]+)\s+      # file permissions
                             ([^/]+)/(\S+)\s+      # user/group
                             (\d+)\s+              # size
                             (\d+)-(\d+)-(\d+)\s+  # Year-month-day
                             ([0-9:]+)\s+          # HH:MM
                             (\S.*)$               # filename
                             """, re.VERBOSE)
    _file_modes = {'l': stat.S_IFLNK, 'd': stat.S_IFDIR, '-': stat.S_IFREG}
    _months = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')
    _pacific = pytz.timezone('US/Pacific')

    def __init__(self, *args):
        self.hpss_path = args[0]
        self.raw_type = args[1]
        self.raw_permission = args[2]
        self.st_nlink = int(args[3])
        self.st_uid = args[4]
        self.st_gid = args[5]
        self.st_size = int(args[6])
        self.raw_dow = args[7]
        self.raw_month = args[8]
        self.raw_day = int(args[9])
        self.raw_hms = args[10]
        self.raw_year = int(args[11])
        self.raw_name = args[12]
        self.ishtar = False
        self._contents = None  # placeholder for htar file contents.
        self._property_cache = dict()
        return

    def __repr__(self):
        return ("HpssFile('{0.hpss_path}', '{0.raw_type}', " +
                "'{0.raw_permission}', {0.st_nlink:d}, '{0.st_uid}', " +
                "'{0.st_gid}', {0.st_size:d}, '{0.raw_dow}', '{0.raw_month}', " +
                "{0.raw_day:d}, '{0.raw_hms}', {0.raw_year:d}, " +
                "'{0.raw_name}')").format(self)

    def __str__(self):
        return self.name

    @property
    def islink(self):
        """``True`` if the file is a symbolic link.
        """
        return self.raw_type == 'l'

    @property
    def isdir(self):
        """``True`` if the file is a directory or a symbolic link that
        points to a directory.
        """
        from .os import stat as hpss_stat
        if self.islink:
            new_path = self.readlink
            if new_path.startswith('/'):
                return hpss_stat(new_path).isdir
            else:
                return hpss_stat(os.path.join(self.hpss_path, new_path)).isdir
        else:
            return self.raw_type == 'd'

    @property
    def readlink(self):
        """Destination of symbolic link.
        """
        if self.islink:
            return self.raw_name.split('->')[1].strip()
        else:
            raise HpssOSError("Invalid argument: '{0}'".format(self.raw_name))

    @property
    def name(self):
        """Name of the file.
        """
        if self.islink:
            return self.raw_name.split('->')[0].rstrip('@ ')
        else:
            return self.raw_name

    @property
    def path(self):
        """Full path to the file.
        """
        return os.path.join(self.hpss_path, self.name)

    @property
    def st_mode(self):
        """File permission mode.
        """
        if 'st_mode' not in self._property_cache:
            try:
                mode = self._file_modes[self.raw_type]
            except KeyError:
                raise AttributeError(("Unknown file type, {0.raw_type}, " +
                                      "for {0.name}!").format(self))
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
        return self._property_cache['st_mode']

    @property
    def st_mtime(self):
        """File modification time.
        """
        if 'st_mtime' not in self._property_cache:
            # seconds = 0
            month = self._months.index(self.raw_month) + 1
            h, m, s = map(int, self.raw_hms.split(':'))
            mtime = int(datetime(self.raw_year, month, self.raw_day,
                                 h, m, s, tzinfo=self._pacific).strftime('%s'))
            self._property_cache['st_mtime'] = mtime
        return self._property_cache['st_mtime']

    def htar_contents(self):
        """Return (and cache) the contents of an htar file.

        Returns
        -------
        :class:`list`
            List containing the contents.
        """
        if self.ishtar:
            if self._contents is None:
                out, err = htar('-t', '-f', self.path)
                self._contents = list()
                for line in out.split('\n'):
                    m = self._htarre.match(line)
                    if m is not None:
                        self._contents.append(m.groups())
            return self._contents
        else:
            return None


def get_hpss_dir():
    """Return the directory containing HPSS commands.

    Returns
    -------
    :class:`str`
        Full path to the directory containing HPSS commands.

    Raises
    ------
    KeyError
        If the :envvar:`HPSS_DIR` environment variable has not been set.
    """
    return os.path.join(os.environ['HPSS_DIR'], 'bin')


def get_tmpdir(**kwargs):
    """Return the path to a suitable temporary directory.

    Resolves the path to the temporary directory in the following order:

    1. If ``tmpdir`` is present as a keyword argument, the value is returned.
    2. If :envvar:`TMPDIR` is set, its value is returned.
    3. If neither are set, ``/tmp`` is returned.

    Parameters
    ----------
    kwargs : :class:`dict`
        Keyword arguments from another function may be passed to this
        function.  If ``tmpdir`` is present as a key, its value will be
        returned.

    Returns
    -------
    :class:`str`
        The name of a temporary directory.
    """
    if 'tmpdir' in kwargs:
        t = kwargs['tmpdir']
    elif 'TMPDIR' in os.environ:
        t = os.environ['TMPDIR']
    else:
        t = '/tmp'
    return t


def hsi(*args, **kwargs):
    """Run :command:`hsi` with arguments.

    Parameters
    ----------
    args : :func:`tuple`
        Arguments to be passed to :command:`hsi`.
    tmpdir : :class:`str`, optional
        Write temporary files to this directory.  Defaults to the value
        returned by :func:`hpsspy.util.get_tmpdir`. This option must be
        passed as a keyword!

    Returns
    -------
    :class:`str`
        The standard output from :command:`hsi`.

    Raises
    ------
    KeyError
        If the :envvar:`HPSS_DIR` environment variable has not been set.
    """
    path = get_hpss_dir()
    ofile = os.path.join(get_tmpdir(**kwargs), 'hsi.txt')
    base_command = [os.path.join(path, 'hsi'), '-O', ofile, '-s', 'archive']
    command = base_command + list(args)
    status = call(command)
    with open(ofile) as o:
        out = o.read()
    if os.path.exists(ofile):
        os.remove(ofile)
    return out


def htar(*args):
    """Run :command:`htar` with arguments.

    Parameters
    ----------
    args : :func:`tuple`
        Arguments to be passed to :command:`htar`.

    Returns
    -------
    :func:`tuple`
        The standard output and standard error from :command:`htar`.

    Raises
    ------
    KeyError
        If the :envvar:`HPSS_DIR` environment variable has not been set.
    """
    outfile = TemporaryFile()
    errfile = TemporaryFile()
    path = get_hpss_dir()
    command = [os.path.join(path, 'htar')] + list(args)
    status = call(command, stdout=outfile, stderr=errfile)
    outfile.seek(0)
    out = outfile.read()
    errfile.seek(0)
    err = errfile.read()
    outfile.close()
    errfile.close()
    return (out.decode('utf8'), err.decode('utf8'))
