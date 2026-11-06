Versions and the Image
======================

The image
---------

The image is built from the doc-builder repository and released with the
action: by default, the action runs in the image of its own version, e.g.
``omnetpp/doc-builder@v1`` in ``ghcr.io/omnetpp/doc-builder:v1``, which is
built from the ``v1`` branch, like the action. To keep the documentation build
stable, use a full version of the action (``omnetpp/doc-builder@v1.2.0``), or
pin an image tag with ``image-tag`` (see the `tags
<https://github.com/orgs/omnetpp/packages/container/package/doc-builder>`__).
``latest`` is the newest image.

The image is ``linux/amd64`` only, so the action runs on Linux runners
(``ubuntu-latest``), with podman or docker.

If you need a build that the action does not do, run your own commands in the
image, with the same tools:

.. code-block:: yaml

   jobs:
     build:
       runs-on: ubuntu-latest
       container: ghcr.io/omnetpp/doc-builder:latest
       steps:
         - uses: actions/checkout@v7
         - run: opp_docgen --format=rst -o doc/ned . && sphinx-build -b html doc _site
         - uses: actions/upload-pages-artifact@v5
           with:
             path: _site

Versions
--------

The image and the action share the versions of the repository. A major version
is a branch (``v1``), and is what a workflow normally uses: it gets fixes and
new features, but no changes that break existing workflows. Those come with a
new major version. Releases are tags ``vMAJOR.MINOR.PATCH`` on it; use one, or
a commit, to pin an exact version.

Each version is also an image tag: the image built from the ``v1`` branch is
``:v1``, that of a release ``:v1.2.0``, and the action runs in the image of its
own version by default.
