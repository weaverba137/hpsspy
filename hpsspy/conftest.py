# Licensed under a 3-clause BSD style license - see LICENSE.rst
# -*- coding: utf-8 -*-
import sys
import locale
import warnings
import importlib
from platform import platform


def pytest_report_header(config):
    """Customize the metadata reported in the pytest header.

    Heavily borrowed from pytest-astropy-header_.

    .. _pytest-astropy-header: https://github.com/astropy/pytest-astropy-header
    """
    try:
        stdoutencoding = sys.stdout.encoding or 'ascii'
    except AttributeError:
        stdoutencoding = 'ascii'

    s = ''

    plat = platform()
    if isinstance(plat, bytes):
        plat = plat.decode(stdoutencoding, 'replace')
    s += f"Platform: {plat}\n\n"
    s += f"Executable: {sys.executable}\n\n"
    s += f"Full Python Version: \n{sys.version}\n\n"

    s += "encodings: sys: {}, locale: {}, filesystem: {}".format(
        sys.getdefaultencoding(),
        locale.getpreferredencoding(),
        sys.getfilesystemencoding())
    s += '\n'

    s += f"byteorder: {sys.byteorder}\n"
    s += "float info: dig: {0.dig}, mant_dig: {0.dig}\n\n".format(
        sys.float_info)

    s += "Package versions: \n"

    for module_name in ('pytz', 'hpsspy'):
        try:
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', category=DeprecationWarning)
                module = importlib.import_module(module_name)
        except ImportError:
            s += f"    {module_name}: not available\n"
        else:
            try:
                version = module.__version__
            except AttributeError:
                version = 'unknown (no __version__ attribute)'
            s += f"    {module_name}: {version}\n"

    return s
