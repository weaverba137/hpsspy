.. hpsspy documentation master file, created by
   sphinx-quickstart on Tue Feb  3 15:49:03 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

==================================
Welcome to HPSSPy's documentation!
==================================

Introduction
++++++++++++

HPSSPy is a Python_ package for interacting with the HPSS_ tape storage
system at NERSC_.  It is currently being developed on GitHub_.

.. _Python: https://www.python.org
.. _HPSS: https://www.nersc.gov/systems/hpss-data-archive/
.. _NERSC: https://www.nersc.gov
.. _GitHub: https://github.com/weaverba137/hpsspy

Requirements
++++++++++++

HPSSPy assumes that the HPSS utilities `hsi and htar`_ are installed.  As of
2023, these utilities are only available within the NERSC_ environment.

.. _`hsi and htar`: https://docs.nersc.gov/filesystems/archive/#common-commands

HPSSPy expects these utilities to exist in the directory ``${HPSS_DIR}/bin``, so
be sure the environment variable :envvar:`HPSS_DIR` is defined.

Contents
++++++++

.. toctree::
   :maxdepth: 1

   configuration
   using
   api
   changes

Indices and tables
++++++++++++++++++

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
