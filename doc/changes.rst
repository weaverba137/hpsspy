=============
Release Notes
=============

0.7.0 (2023-07-14)
------------------

* :command:`missing_from_hpss` will proceed through all stages, even if
  serious errors are detected, to facilitate batch processing. The older
  behavior can be enabled with ``--exit-on-error`` (PR `#15`_).
* Fix error handling for a variety of corner cases (PR `#15`_).
* Increase test coverage to 100% (PR `#15`_).

.. _`#15`: https://github.com/weaverba137/hpsspy/pull/15

0.6.1 (2022-05-20)
------------------

* Bumped version due to malformed PyPI upload.

0.6.0 (2022-05-20)
------------------

* Reorganization of package structure and metadata; no changes to user-facing API.
* Support full-precision timestamps on HPSS files (PR `#14`_).

.. _`#14`: https://github.com/weaverba137/hpsspy/pull/14

0.5.1 (2019-08-20)
------------------

* Unused patterns and over-large backup files
  no longer trigger a critical error (PR `#12`_).

.. _`#12`: https://github.com/weaverba137/hpsspy/pull/12

0.5.0 (2019-05-18)
------------------

*This release drops support for Python 2.*

* Remove all Python 2 code (PR `#8`_).
* Support fine-grained exclusion in configuration files (PR `#10`_).
* Avoid commonly-used names for metadata in configuration files (PR `#10`_).
* Detect newer files on disk that map to older HPSS files (PR `#10`_).
* Allow top-level directories to contain only files (PR `#10`_).

.. _`#8`: https://github.com/weaverba137/hpsspy/pull/8
.. _`#10`: https://github.com/weaverba137/hpsspy/pull/10

0.4.2 (2019-01-29)
------------------

* Further fixes for mapping HTAR file names back to directories (PR `#6`_).

.. _`#6`: https://github.com/weaverba137/hpsspy/pull/6

0.4.1 (2019-01-16)
------------------

* Handle directory names that contain underscore characters; improve test
  coverage (PR `#4`_).

.. _`#4`: https://github.com/weaverba137/hpsspy/pull/4

0.4.0 (2017-08-10)
------------------

* Add ``--version`` option.
* Add Python 3.6, remove 3.3.
* Add many quality-assurance checks and additional documentation (PR `#2`_).

.. _`#2`: https://github.com/weaverba137/hpsspy/pull/2

0.3.0 (2017-01-18)
------------------

* General refresh of Python code, documentation, test suite.  However,
  no major changes to the API.
* Command-line inputs are no longer rigidly restricted to SDSS or DESI.

0.2.1 (2015-04-22)
------------------

* Fixed some setup.py errors, no code changes.

0.2.0 (2015-04-22)
------------------

* Moved configuration items to JSON files.
* Started adding support for DESI.
* Add tests to util subpackage.
* Add ``__future__`` statements.
* Clean up API documentation.
* Minor bug fixes.

0.1.0 (2015-03-25)
------------------

* Initial release.  Used to scan all SDSS data.
