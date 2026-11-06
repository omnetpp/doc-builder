The Theme
=========

``omnetpp_immaterial`` is a Sphinx extension on top of ``sphinx_immaterial``,
the shared look of the OMNeT++ sites: denser sidebars with resizable widths, a
sticky tab bar whose tabs open their sections as menus, the name of the site
next to the logo, and a footer crediting OMNeT++. The image has it, so a
project built in the image enables it in its ``conf.py``:

.. code-block:: python

   html_theme = 'sphinx_immaterial'
   extensions = [..., 'sphinx_immaterial', 'omnetpp_immaterial']

The settings of ``sphinx_immaterial`` itself (``html_theme_options``: colors,
features, the repository link, ...) are in its `documentation
<https://jbms.github.io/sphinx-immaterial/>`__; the ``conf.py`` of this site
(see :doc:`../guide/sphinx-site`) has a light and a dark palette and a link to
the repository.

Settings
--------

All are optional. The navigation settings are explained, with this site as the
example, in :doc:`navigation`.

.. list-table::
   :header-rows: 1
   :widths: 25 10 65

   * - Setting
     - Default
     - Meaning
   * - ``omnetpp_homepage``
     - ``None``
     - URL that the logo and the name of the site in the header lead to
   * - ``omnetpp_nav_nowrap``
     - ``[]``
     - URL path parts (e.g. ``'/api/'``) whose sidebar entries scroll sideways
       instead of wrapping
   * - ``omnetpp_nav_menus``
     - ``True``
     - the tabs open their sections as menus
   * - ``omnetpp_nav_menu_depth``
     - ``3``
     - levels of submenus
   * - ``omnetpp_nav_no_menu``
     - ``[]``
     - tab titles that open no menu
   * - ``omnetpp_nav_dropdown``
     - ``False``
     - tab titles (or ``True`` for all) navigated by their menus alone,
       without the navigation sidebar
   * - ``omnetpp_privacy_url``
     - ``None``
     - URL of the privacy policy of the site, linked from the footer
   * - ``omnetpp_commit``
     - ``None``
     - the commit the pages were built from, named in the footer (e.g.
       ``'81a07d40ef'``)
   * - ``omnetpp_nav_json_threshold``
     - ``100``
     - a document whose toctree lists more documents gets a navigation tree
       loaded as JSON (``0`` or ``None``: none by size)
   * - ``omnetpp_nav_json``
     - ``[]``
     - documents that get one regardless of size, e.g. ``['api/index']``
   * - ``omnetpp_nav_json_exclude``
     - ``[]``
     - documents that never get one

The footer
----------

The footer names the commit that the pages were built from, as on this site.
The ``conf.py`` of this site takes it from git, with a ``+`` if tracked files
have changes that are not committed:

.. code-block:: python

   omnetpp_commit = os.popen('git rev-parse --short=10 HEAD').read().strip()
   if omnetpp_commit and os.popen('git status --porcelain --untracked-files=no').read():
       omnetpp_commit += '+'
   omnetpp_commit = omnetpp_commit or None

Untracked files are not counted, because the output of the build is among
them while it runs, unless it is in ``.gitignore``.

With the theme's cookie consent configured (``html_theme_options['consent']``),
the footer also links to the consent dialog, so that the reader can change
their choice.

Pages
-----

A page whose top has a ``:no-copy:`` field gets no copy buttons on its code
blocks: the theme lays out the whole page for each button, which freezes the
browser for minutes on a page with thousands of code blocks (e.g. a
single-page manual or a large generated reference).

A page outside every toctree, or below the root of a navigation tree loaded as
JSON, still gets its table of contents, which the theme takes from the page's
entry in the navigation. That is for generated references such as the NED
reference, whose type and file pages are in no toctree.

Images in the dark scheme
-------------------------

Charts, diagrams and screenshots with a transparent background are drawn for a
light page, so in the dark scheme a PNG image whose top left or top right pixel
is transparent gets a white, padded background (the ``transparent-image``
class); one up to 32 pixels wide, e.g. an icon in a table, gets it without the
padding (``transparent-icon``), keeping its size. An SVG image in black, white
and grays only, e.g. a diagram of modules, is inverted instead
(``adaptive-image``), which makes it light on the dark page like the text; one
with colors or a bitmap in it, e.g. a chart, gets the white background unless
it paints one of its own. A figure whose ``:class:`` option names one of these
classes keeps it. Switch this site to the dark scheme (the bulb in the header)
and open a type of the :doc:`NED Reference <../ned/index>` to see it.

Restyling
---------

A site restyles the theme with its own stylesheet (``html_css_files``); e.g.
``--omnetpp-tabs-edge`` is the height of a bottom border that the site gives
the tab bar, which stays below the header while the tab bar is away.
