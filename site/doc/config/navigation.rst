Navigation
==========

The tabs of a site are the entries of the toctrees of its root document. With
``omnetpp_immaterial``, each tab opens its pages as a menu when the pointer is
on it, with submenus down to ``omnetpp_nav_menu_depth`` levels; the page shows
the pages of its tab in the navigation sidebar on the left. The settings below
change this for some tabs, by their titles, or for the whole site.

This site
---------

Each tab of this site is navigated in another way:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Tab
     - What it shows
     - Setting
   * - Home
     - no menu: it is a single page
     - ``omnetpp_nav_no_menu = ['Home']``
   * - Getting Started
     - a menu, and the navigation sidebar
     - (the default)
   * - Configuration
     - a menu, and no navigation sidebar, which gives its width to the content
       (this page)
     - ``omnetpp_nav_dropdown = ['Configuration']``
   * - Reference
     - a menu, and the trees of the NED reference and the C++ API in the
       sidebar, whose entries scroll sideways
     - ``omnetpp_nav_nowrap = ['/ned/', '/api/']``,
       ``omnetpp_nav_json = ['api/index']``

The settings that apply to the whole site, e.g. ``omnetpp_nav_menus = False``
for no menus at all, are shown by the :doc:`variants` of the site.

The root document of this site makes the tabs: a toctree of the page itself
for Home, one of the Getting Started and Configuration pages, which are
named by their titles, and one captioned Reference:

.. code-block:: rst

   .. toctree::
      :caption: Home
      :hidden:

      self

   .. toctree::
      :hidden:

      guide/index
      config/index

   .. toctree::
      :caption: Reference
      :hidden:

      NED Reference <ned/index>
      C++ Reference <api/index>

Menus
-----

``omnetpp_nav_menus`` (``True``) makes the tabs open their pages as menus,
which are built from the navigation that each page carries, so they need no
setting. ``omnetpp_nav_menu_depth`` (``3``) is the depth of their submenus.
``omnetpp_nav_no_menu`` names the tabs that open none, such as the tab of a
single page, whose menu would only repeat the tab. The menus are on wide
screens only; on a narrow one, the theme's drawer navigates the site.

The sidebar
-----------

``omnetpp_nav_dropdown`` names the tabs whose pages show no navigation sidebar
on wide screens, or is ``True`` for all tabs: their menus are the navigation,
and the content is wider. It suits a tab of a few pages with wide tables or
code, like this one; a tab whose pages are found in a tree, like the Reference,
needs the sidebar.

``omnetpp_nav_nowrap`` lists parts of URL paths whose sidebar entries scroll
sideways instead of wrapping: the long names of types and classes in a
reference are easier to read on one line.

The reader sets the widths of the sidebar and of the content by dragging their
edges, for every page of the site and later visits.

Trees loaded as JSON
--------------------

The large generated references of a site (a NED reference, a C++ API) get
their navigation from a tree loaded as JSON. The navigation that every page of
the site carries ends at the root of the reference (the document whose toctree
lists its pages); the tree of the root is written once, to
``_static/omnetpp-nav/``, and a script renders it in the sidebar of the pages
below the root, opening a group only when the reader expands it. Without it,
each page of the site would carry an entry for every page of the reference:
hundreds of kilobytes per page, and a build time that grows with the square of
the number of pages.

The roots are found without any setting: ``omnetpp_neddoc`` supplies the tree
of its reference (its packages, namespaces and categories with their types, and
its files); a document whose toctree lists more than
``omnetpp_nav_json_threshold`` documents (e.g. the ``api/index`` of the action)
gets its doxygen classes by namespace, and its topics and files, when there is
a doxygen ``tagfile.xml`` next to it, and the tree of its toctree otherwise.
``omnetpp_nav_json`` and ``omnetpp_nav_json_exclude`` name documents that get
one regardless of size, or never. The C++ API of this site has only a few
classes, so its ``conf.py`` names ``api/index`` in ``omnetpp_nav_json`` to show
the tree that a large API gets. A page listed twice (e.g. a type under its
package and its category) opens in the group that the reader clicked it in.
