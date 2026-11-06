A Sphinx Site
=============

With ``sphinx-source``, the site is built from your Sphinx project, and the NED
reference (and the C++ API) become pages of it:

.. code-block:: yaml

         - uses: omnetpp/doc-builder@v1
           with:
             sphinx-source: doc
             doxygen: true

The action generates the NED reference as reStructuredText into
``<sphinx-source>/ned`` (``ned-dir``) and the C++ API into
``<sphinx-source>/api`` (``api-dir``), then runs ``sphinx-build`` in the Sphinx
project. Your project refers to them from a toctree:

.. code-block:: rst

   .. toctree::

      guide
      NED Reference <ned/index>
      C++ Reference <api/index>

and ignores them in git, since they are generated (``doc/.gitignore``):

.. code-block:: text

   /ned/
   /api/

The configuration
-----------------

The action does not change ``conf.py``; it is yours. The image provides Sphinx,
``sphinx_immaterial`` and the OMNeT++ extensions (see :doc:`../config/theme`
and :doc:`../config/extensions`). A ``conf.py`` that gives the site the look of
the OMNeT++ sites:

.. code-block:: python

   project = 'My Model'

   extensions = [
       'sphinx_immaterial',
       'omnetpp_immaterial',   # the look of the OMNeT++ sites
       'omnetpp_neddoc',       # the :ned: and :msg: roles, NED/MSG highlighting
       'omnetpp_doxylink',     # the :cppref: role (with doxygen: true)
   ]
   html_theme = 'sphinx_immaterial'

   doxylink = {'cppref': ('api/tagfile.xml', 'api/')}

``omnetpp_neddoc`` finds the NED reference in ``ned`` (its ``neddoc_dir``
setting; change it together with ``ned-dir``).

The NED reference and the C++ API have a page per type, too many for the
navigation that Sphinx puts into every page. ``omnetpp_immaterial`` shows them
in the sidebar as trees that the browser loads when the reader opens them: the
NED reference by packages, kinds of types and files, the C++ API by namespaces
and classes. The trees appear under the entries of ``ned/index`` and
``api/index`` in your toctree; open the :doc:`NED Reference <../ned/index>` of
this site to see them.

The pages of the site refer to NED and MSG types and to C++ classes with roles,
and highlight NED, MSG and ini code (see :doc:`../config/writing`).

This site as an example
-----------------------

The `site/doc
<https://github.com/omnetpp/doc-builder/tree/v1/site/doc>`__ directory of the
repository is the Sphinx project of this site. Its ``conf.py``:

.. literalinclude:: ../conf.py
   :language: python

To build the site locally while writing it, see :doc:`local`.
