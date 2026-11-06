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

Pull the image again to update it:

.. code-block:: bash

   podman pull ghcr.io/omnetpp/doc-builder:latest

Inside a container that is the image (``ENGINE=none``), it runs the tools
directly.

This site, from the root of the doc-builder repository:

.. code-block:: bash

   ./doc-builder.sh --project-dir site --title "Sample Model" \
       --sphinx-source site/doc --doxygen --pdf
