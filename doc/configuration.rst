====================
HPSSPy Configuration
====================

Introduction
++++++++++++

The primary HPSSPy command-line program :command:`missing_from_hpss` is
configured with a JSON_ file.  Both the JSON standard and the
Python :mod:`json` library are very strict.  There is a very quick way
to check the validity of JSON files however::

    python -c 'import json; j = open("config.json"); data = json.load(j); j.close()'

where ``"config.json"`` should be replaced with the name of the file to be
tested.

The top-level JSON container should be an "object", equivalent to a Python
:class:`dict`.  The simplest possible file that satisfies this requirement
is::

    {
    }

Obviously, that's not very much to go on.  You will need further data
described below.

.. _JSON: http://json.org

Metadata
++++++++

The configuration file should contain a top-level keyword ``"__config__"``.
The value should itself be a :class:`dict`, containing some important
metadata::

    {
        "__config__": {
            "root": "/global/project/projectdirs/my_project",
            "hpss_root": "/nersc/projects/my_project",
            "physical_disks": ["my_project"]
        }
    }

root/
    The directory that contains *all* the data associated with the project.

hpss\_root/
    The path on the HPSS tape system that will contain the backups.

physical\_disks/
    If the data are spread across several physical disks and linked into
    the root path via symlinks, the various physical disks need to be listed
    here.  If the value is equivalent to ``False``, *e.g.*,
    [``null``, ``false``, ``[]``] this is means that the
    ``"root"`` disk contains all the physical data.  If the value of
    is equivalent to a one-item list containing ``os.path.basename(root)``,
    then this *also* means that the ``"root"`` disk contains all the physical
    data.  A list of simple names generates the physical disks by
    substitution on the basename of the ``"root"`` value.  More complicated
    configurations are possible, see :func:`hpsspy.scan.physical_disks`.

Sections
++++++++

Inside the root directory, as described above, there may be several top-level
directories.  For the purposes of this documentation, these are called
"sections" or "releases".  The terms are interchangeable.  Each section
has configuration items that describe its structure::

    {
        "__config__": {
            "root": "/projects/my_project",
            "hpss_root": "/hpss/projects/my_project",
            "physical_disks": ["my_project"]
        },
        "data": {
            "__exclude__": [],
            "d1": {
                "d1/batch/.*$": "d1/batch.tar",
                "d1/([^/]+\\.txt)$": "d1/\\1",
                "d1/templates/[^/]+$": "d1/templates/templates_files.tar"
            }
        }
    }

The :command:`missing_from_hpss` command works on one section at a time.
The name of the section is passed on the command-line::

    missing_from_hpss config.json data

This would read the ``"data"`` section above.

Each section should have an ``"__exclude__"`` keyword, whose value is a list
of files to be ignored.  In the example above, in order to ignore the file
``/projects/my_project/data/d1/README.html``, the ``"__exclude__"`` value
would be ``["d1/README.html"]``.  Note that this is relative to the
path ``/projects/my_project/data``, since ``"data"`` is the section being
processed.  Generally, this should only be used for a handful of top-level
files, like README files.  For more precise exclusion, see the ``"EXCLUDE"``
statement below.

In the special case where a section contains only files, and no
subdirectories, the special pseudo-subdirectory ``"__top__"`` can be
used to contain the configuration.

Mapping File Names to HPSS Archives
+++++++++++++++++++++++++++++++++++

Within a section, each immediate subdirectory should be described with
a keyword in the configuration file.  :command:`missing_from_hpss` will
complain if not, but it won't necessarily cause it to fail.  In the
example above, ``/projects/my_project/data/d1`` is configured.

There are many possible ways to bundle files for archiving.  Generally you
want to make archives as large as possible, without spilling onto multiple
tapes.  However, with highly structured, deeply-nested directory structures,
this isn't always the best way to do it from a data *retrieval* viewpoint.

Consider this scenario.  ``/projects/my_project/data`` has been archived to
ten tape archives called ``data00.tar``, ``data01.tar``, ... ``data09.tar``.
The file ``/projects/my_project/data/d1/templates/d1_template_05.fits``
needs to be recovered.  Which tape archive contains it?

Now consider the scenario where the files in
``/projects/my_project/data/d1/templates`` have been archived to
``/hpss/projects/my_project/data/d1/templates/d1_templates_files.tar``.
Now is it easier to recover the file?

One should still try to make archives as big as possible, but generally
speaking, long-term archiving of large, complex data sets should be
done by **someone who actually knows the structure of the data set** .

In coding terms we describe a portion of a directory tree hierarchy
using regular expressions to match *files* in that portion.  Then we map
files that match that regular expression to tape archive files.

Finally, it should be noted that the configuration of each section is
organized by subdirectory in order to speed up the process of mapping files
to backup files.  Instead of looking through every possible configuration
of files, only the configurations in a subdirectory need to be considered
when examining files in that subdirectory.

Regular Expression Details
++++++++++++++++++++++++++

The HPSSPy package, and :command:`missing_from_hpss` will validate the
regular expressions used in the configuration file, in addition to checking
the overall validity of the JSON file itself.  That is, a bad regular
expression will be rejected before it has any chance to "touch" any real data.

The regular expressions should follow Python's conventions,
described in :mod:`re`.  In addition to those conventions, this package
imposes some additional requirements, conventions and idioms:

* Requirements

  - Backslashes must be escaped in JSON files.  For example the
    metacharacter (match a single decimal digit) ``\d`` becomes ``\\d``.
  - Regular expressions should end with the end-of-line marker ``$``.

* Conventions

  - Any archive file name ending in ``.tar`` is assumed to be an HTAR file,
    and that command will be used to construct it.
  - Any archive file *not* ending in ``.tar`` will simply be copied to
    HPSS as is.
  - The special string ``"EXCLUDE"`` can be used to prevent backups of
    parts of a directory tree that might otherwise be archival. For example,
    ``"d1/data/preproc/.*$" : "EXCLUDE"`` would prevent the ``preproc``
    directory from being backed up, even if other parts of ``d1/data``
    were configured for backup.
  - The special string ``"AUTOMATED"`` behaves the same way as ``"EXCLUDE"``,
    but is a human-readable way to denote data sets that are backed up by
    automation independently of :command:`missing_from_hpss`, as opposed
    to not being backed up at all.
  - When constructing an archive file, :command:`missing_from_hpss` will
    obtain the directory it needs to archive from the name of the *archive*
    file, not the regular expression itself.  This is because regular
    expression *substition* is performed on the archive file name.
    For example ``batch.tar`` means "archive a batch/ directory".
    For longer file names, any "prefix" of the file name will be stripped
    off, and the "suffix" of the file will be used. For example,
    ``d1/data_d1_batch.tar`` also means "archive a batch/ directory", because
    ``data_d1_`` recognized as a prefix and stripped off.  In particular,
    this allows directory names to contain underscores.
  - An archive filename that ends with ``_files.tar``, *e.g.* ``foo/bar_files.tar``
    is a signal to :command:`missing_from_hpss` to construct
    the archive file in a certain way, not by descending into a directory,
    but by constructing an explicit list of files and building an archive
    file out of that.

* Idioms

  - Archive the entire contents of a directory into a single file:
    ``"foo/.*$" : "foo.tar"``.
  - Archive several subdirectories of a directory, each into their own file:
    ``"foo/(bar|baz|flub)/.*$" : "foo/foo_\\1.tar"``.  The name of the
    directory matched in parentheses will be substituted into the file name.
  - Archive arbitrary subdirectories of a *set* of subdirectories:
    ``"d1/foo/(ab|bc|cd|de|ef)/([^/]+)/.*$" : "d1/foo/\\1/d1_foo_\\1_\\2.tar"``
  - Match files in a directory, but not any files in any
    subdirectory: ``"foo/[^/]+$" : "foo_files.tar"``.  See also the
    ``_files.tar`` convention mentioned above.
  - Group some but not all subdirectories in a directory into a single
    archive file for efficiency: ``"foo/([0-9])([0-9][0-9])/.*$" : "foo/foo_\\1XX.tar"``.
    Note the ending of the archive file, and that the directories have to
    have a very uniform naming convention (three and only three digits
    in this example).  Also, the placeholder ``X`` needs to be at the *end* of
    the file name.
  - Do not create an archive file, just copy the file, as is, to HPSS:
    ``"d1/README\\.txt$" : "d1/README.txt"``.  Similarly, for a set of TXT files:
    ``"d1/([^/]+\\.txt)$" : "d1/\\1"``.
  - An example with lots of substitutions::

        "d1/foo/([0-9a-zA-Z_-]+)/sub-([0-9]+)/([0-9]+)/.*$" : "d1/foo/\\1/spectra-\\2/\\1_spectra-\\2_\\3.tar"

Finally, for truly monumentally-complicated directory trees, there is a
`JSON file`_ included with this distribution describing the SDSS_ data tree
that can be used for examples.  To view the equivalent files and directories
for section ``"dr12"``, for example, visit https://data.sdss.org/sas/dr12.

.. _SDSS: https://www.sdss.org
.. _`JSON file`: https://github.com/weaverba137/hpsspy/blob/master/hpsspy/data/sdss.json
