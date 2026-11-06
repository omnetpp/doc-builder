Installation
============

The action needs no installation: a workflow of your model's repository uses
it, and GitHub fetches it. This page publishes the NED reference of a model;
:doc:`sphinx-site` adds your own pages.

The workflow
------------

``.github/workflows/docs.yml`` in your model repository:

.. code-block:: yaml

   name: Documentation

   on:
     push:
       branches: [master]
     workflow_dispatch:

   concurrency:
     group: pages
     cancel-in-progress: false

   jobs:
     build:
       runs-on: ubuntu-latest
       permissions:
         contents: read
       steps:
         - uses: actions/checkout@v7
         - uses: omnetpp/doc-builder@v1

     deploy:
       needs: build
       runs-on: ubuntu-latest
       permissions:
         pages: write
         id-token: write
       environment:
         name: github-pages
         url: ${{ steps.deployment.outputs.page_url }}
       steps:
         - id: deployment
           uses: actions/deploy-pages@v5

The deployment is a second job, because it needs permissions that the build
does not.

Enabling GitHub Pages
---------------------

Once, in the settings of the repository: **Settings → Pages → Build and
deployment → Source: GitHub Actions**. The next run of the workflow publishes
the site, at ``https://<owner>.github.io/<repository>/``.

What it publishes
-----------------

The NED reference of the project, in the repository root, in the look of the
NED documentation of the Eclipse-based IDE (``ned-format: html-material``;
``html-readthedocs`` and ``html`` are the other choices). The NED folders of
the project are taken from its ``.nedfolders`` file, like in the IDE.

.. only:: html and not variant

   The `NED-only variant <../variants/ned-only/index.html>`__ of this site is
   what it looks like.

Add ``doxygen: true`` to also publish the C++ API, under ``api/``. The NED
types' pages then link to their C++ classes ("C++ definition"):

.. code-block:: yaml

         - uses: omnetpp/doc-builder@v1
           with:
             doxygen: true

The workflow of this site
-------------------------

This site is deployed by the workflow below, from the ``site/`` directory of
the doc-builder repository. It builds the site three times: the site itself,
with the C++ API and a PDF, and two :doc:`variants <../config/variants>` of it
into subdirectories, so it uploads the Pages artifact itself.

.. literalinclude:: ../../../.github/workflows/pages.yml
   :language: yaml
