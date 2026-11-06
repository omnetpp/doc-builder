The C++ API
===========

``doxygen: true`` runs doxygen with a bundled configuration (that of the
OMNeT++ API documentation, with `doxygen-awesome
<https://github.com/jothepro/doxygen-awesome-css>`__) on the header files
under ``<project-dir>/src`` (``doxygen-input``; generated ``*_m.h`` files are
excluded). Undocumented classes and members are left out.

``doxyfile`` replaces the bundled configuration with yours. Either way, the
action overrides the output settings (``OUTPUT_DIRECTORY``, ``HTML_OUTPUT``,
``GENERATE_TAGFILE``, ...), and, in a Sphinx site, those that the wrapping of
the pages into the site needs (``GENERATE_TREEVIEW = NO``, ``DISABLE_INDEX =
NO``, ``SEARCHENGINE = NO``). Paths in the doxyfile are relative to the working
directory, i.e. the repository root.

In a Sphinx site
----------------

The doxygen pages are wrapped into Sphinx pages by ``doxysphinx``, like in the
OMNeT++ documentation, without doxygen's own title and navigation bar, and
``api/index`` is the class list, titled "<title> C++ Reference". Only the
overview pages (class hierarchy, class index, namespace list) and the topic
pages are in the site navigation, under ``api/index``; the class, namespace
and file pages are not, so that a large API does not add an entry per class to
the navigation of every page. The tree of the C++ API in the sidebar lists them
instead.

Doxygen comments can contain reStructuredText between ``\rst`` and
``\endrst``.

The :doc:`C++ Reference <../api/index>` of this site is the API of the sample
model, four classes in two namespaces.
