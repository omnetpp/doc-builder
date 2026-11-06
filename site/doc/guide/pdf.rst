PDF
===

With ``pdf: true``, the action also builds the Sphinx project with
``sphinx-build -M latexpdf`` (the image has TeX Live), and copies the PDFs into
the root of the site, where the pages can link to them. Without
``sphinx-source`` there is no PDF: ``opp_docgen`` writes none.

A PDF of a part of the site
---------------------------

What goes into a PDF is up to ``latex_documents`` in ``conf.py``: each entry
is a PDF, whose root document is the start of its toctree. The NED reference
and the C++ API are pages for the web, so let the root be a document whose
toctree does not include them, e.g. that of a guide:

.. code-block:: python

   latex_documents = [('guide/index', 'my-model.tex', 'My Model Guide', author, 'manual')]

The PDF of this site is built this way from its Getting Started pages, the
toctree of ``guide/index``:

.. literalinclude:: ../conf.py
   :language: python
   :start-at: latex_documents

.. only:: html and not variant

   It is `doc-builder.pdf <../doc-builder.pdf>`__, in the root of the site.

Links in the PDF
----------------

Links to pages that are not in the PDF (e.g. from the guide to the NED
reference) become their text. A ``:cppref:`` link to the C++ API on the site
by a relative path (``doxylink = {'cppref': ('api/tagfile.xml', 'api/')}``)
cannot work in a PDF either: it also becomes its text, with a warning, which
fails the build with ``fail-on-warnings``. Keep ``:cppref:`` out of the PDF's
documents, as this site does, or give doxylink the API's URL, e.g. the
published site's, and the PDF links there:

.. code-block:: python

   doxylink = {'cppref': ('api/tagfile.xml', 'https://example.org/my-model/api/')}
