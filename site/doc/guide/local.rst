Running Locally
===============

``doc-builder.sh`` is the whole action; it runs the same build on your machine,
with podman (or docker: ``ENGINE=docker``). From the repository root of your
model, with a checkout of the doc-builder repository next to it:

.. code-block:: bash

   ../doc-builder/doc-builder.sh --sphinx-source doc --doxygen

It takes the inputs of the action as options (``--help`` lists them), and
builds into ``_site``, which you can open in a browser or serve with:

.. code-block:: bash

   python3 -m http.server -d _site

``--serve`` serves the site at http://localhost:8000/ (``--port`` changes the
port) until you press Ctrl-C. With a Sphinx project, a page you change is
rebuilt, and the browser reloads it.

Working on the pages
--------------------

The NED reference and the C++ API are most of the build time of a large
model. ``--ned=false`` (and no ``--doxygen``) builds only the pages of the
Sphinx project, which takes seconds:

.. code-block:: bash

   ../doc-builder/doc-builder.sh --sphinx-source doc --ned=false --serve

The references that are not built are removed from the Sphinx project, where
an earlier build generated them, so that the build does not read their old
pages. Sphinx then warns about toctree entries that point to them, and
``:ned:`` names render as plain literals with one ``neddoc.no_reference``
warning. To drop those entries from the menu without warnings, exclude the
missing references at the end of ``conf.py``, after ``exclude_patterns`` and
``suppress_warnings`` are set, if only to ``[]`` (``ned`` and ``api`` are
``ned-dir`` and ``api-dir``):

.. code-block:: python

   for ref in ('ned', 'api'):
       if not os.path.exists(os.path.join(ref, 'index.rst')):
           exclude_patterns.append(ref + '/**')
           suppress_warnings.append('toc.excluded')
   if not os.path.exists('ned/index.rst'):
       suppress_warnings.append('neddoc.no_reference')

Sphinx leaves a toctree entry to an excluded page out of the menu, and warns
about it as ``toc.excluded``, which in such a build only the references are.
``omnetpp_doxylink`` still warns once that the tag file of the C++ API is
missing.

Pull the image again to update it:

.. code-block:: bash

   podman pull ghcr.io/omnetpp/doc-builder:latest

Inside a container that is the image (``ENGINE=none``), it runs the tools
directly.

This site, from the root of the doc-builder repository:

.. code-block:: bash

   ./doc-builder.sh --project-dir site --title "Sample Model" \
       --sphinx-source site/doc --doxygen --pdf
