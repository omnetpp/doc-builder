Variants of This Site
=====================

Some settings apply to the whole site, so one site cannot show them side by
side. The workflow of this site (see :doc:`../guide/installation`) builds it
again with other settings, into subdirectories of the same deployment.

.. only:: not variant

   .. list-table::
      :header-rows: 1
      :widths: 25 75

      * - Variant
        - How it is built
      * - `No menus <../variants/no-menus/index.html>`__
        - The same Sphinx project with ``sphinx-args: -t variant -D
          omnetpp_nav_menus=0``: the tabs open no menus, and the pages are
          found in the navigation sidebar. ``-t variant`` hides the links of
          this table, which lead out of the variant.
      * - `NED reference only <../variants/ned-only/index.html>`__
        - No ``sphinx-source``: the NED reference and the C++ API alone, as
          ``opp_docgen`` writes them (``ned-format: html-material``). This is
          what the workflow of :doc:`../guide/installation` publishes.

.. only:: variant

   This page is part of a variant; the `variants
   <https://omnetpp.org/doc-builder/config/variants.html>`__ are linked from
   the main site.

``sphinx-args`` passes options to ``sphinx-build``: ``-D`` overrides a setting
of ``conf.py``, and ``-t`` sets a tag that the pages and ``conf.py`` can test
(``.. only::``, ``tags.has()``).
