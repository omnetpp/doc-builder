The Extensions
==============

The image has these Sphinx extensions besides the theme; a project enables
them in its ``conf.py``. Their use in pages is shown in :doc:`writing`.

omnetpp_neddoc
--------------

Works with the NED reference that the action (``opp_docgen --format=rst``)
generates into the Sphinx project. Its ``:ned:`` and ``:msg:`` roles link type
names to the pages of the reference, by the full name or the short one, from
the ``nedtags.xml`` and ``msgtags.xml`` tag files that ``opp_docgen`` writes
next to the pages; an ambiguous short name links to the first type in the tag
file, and a name that is not there is a warning. In HTML, it inlines the
diagrams of the reference pages, so that the types in them link to their
pages, and gives them the colour scheme of ``sphinx_immaterial``; a diagram
shrinks to the width of the page down to 80% of its size, and a wider one
scrolls sideways. It also sets up ``omnetpp_lexers``, for the ``ned`` and
``msg`` code blocks of the reference.

The ``index`` page of the reference has the overview pages (packages, modules,
files, ...) in its toctree; the type and file pages are reached from their
listings, and are in no toctree. With ``omnetpp_immaterial``, the sidebar of
the reference pages shows the reference as a tree (see :doc:`navigation`).

.. code-block:: python

   extensions = [..., 'omnetpp_neddoc']
   neddoc_dir = 'ned'   # where the reference is, relative to the Sphinx project

.. list-table::
   :header-rows: 1
   :widths: 20 10 70

   * - Setting
     - Default
     - Meaning
   * - ``neddoc_dir``
     - ``'ned'``
     - the directory of the reference in the Sphinx project (the action's
       ``ned-dir``)
   * - ``neddoc_tags_dir``
     - ``None``
     - where the tag files are, if not in ``neddoc_dir``; relative to the
       Sphinx project, or absolute
   * - ``neddoc_url``
     - ``None``
     - URL of the root of a reference published by another build (e.g.
       another version), which the roles then link to with absolute URLs; its
       tag files are in ``neddoc_tags_dir``

A name that is not in the tag files is a warning of type ``neddoc.unknown``,
and one whose page is not in the build is a ``neddoc.missing``; both render as
plain literals. A build without tag files warns once, with
``neddoc.no_reference``. A site silences them with ``suppress_warnings``.

omnetpp_doxylink
----------------

The extension behind the ``:cppref:`` role, a fork of `sphinxcontrib-doxylink
<https://github.com/sphinx-contrib/doxylink>`__: it defines roles that link C++
symbols to the pages of a doxygen API, looked up in doxygen's tag file. Unlike
the original, it can leave the symbols of external libraries unlinked without
a warning.

.. code-block:: python

   extensions = [..., 'omnetpp_doxylink']
   doxylink = {'cppref': ('api/tagfile.xml', 'api/')}

A name matches the symbols that end in it; an argument list, if given, selects
among overloads and must match the declaration's, ``const`` included. In a PDF,
a link to the doxygen HTML by a relative path becomes its text, with a warning
(see :doc:`../guide/pdf`); one by a URL links there.

.. list-table::
   :header-rows: 1
   :widths: 30 10 60

   * - Setting
     - Default
     - Meaning
   * - ``doxylink``
     - ``{}``
     - role name → ``(tag file, doxygen HTML root)``, optionally with a third
       element, the doxygen PDF that the LaTeX builder links to instead; the
       tag file is a path relative to the Sphinx project, or a URL; the HTML
       root is relative to the Sphinx project, absolute, or a URL
   * - ``doxylink_external_namespaces``
     - ``[]``
     - namespaces (e.g. ``'std'``) whose symbols are intentionally not in the
       tag file; references to them render as plain code without a warning
   * - ``doxylink_pdf_files``
     - ``{}``
     - PDF name (the third element above) → URL or path to fetch it from into
       the LaTeX output
   * - ``doxylink_parse_error_ignore_regexes``
     - ``[]``
     - regular expressions matched against the warnings about tag file
       entries whose argument list cannot be parsed

omnetpp_lexers
--------------

Adds the Pygments lexers of the OMNeT++ file formats as code-block languages:
``ned``, ``msg``, ``ini`` (in place of Pygments' own, also recognizing
``include`` lines) and ``fp`` (fingerprint test output). It has no settings,
and ``omnetpp_neddoc`` sets it up.

.. code-block:: python

   extensions = [..., 'omnetpp_lexers']

omnetpp_media
-------------

Adds directives that embed videos and audio in HTML: ``video`` (looping) and
``video_noloop`` for a local file or a URL, ``audio``, and ``youtube`` and
``vimeo`` for the id of a video there. All take the ``width``, ``height`` and
``align`` (``left``, ``center`` or ``right``, the default) options, and their
content is the caption. A local file is resolved relative to the document,
like an image; a URL, or a path that starts with a slash, is used as it is.
The other formats, e.g. a PDF, show the caption instead, with a link to
YouTube or Vimeo. This site does not use it, to embed no third-party content.

.. code-block:: python

   extensions = [..., 'omnetpp_media']

.. code-block:: rst

   .. youtube:: KUe_vrWbEJY
      :width: 560
      :height: 315

      Introduction to the Simulation IDE

   .. video:: media/run.mp4
      :width: 640
