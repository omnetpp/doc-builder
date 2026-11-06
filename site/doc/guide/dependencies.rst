Models That Build on Other Models
=================================

A model that uses the NED types of another one (e.g. INET) needs the other's
NED files, to resolve the types it uses. They are not documented, but linked
to, if you tell where their documentation is:

.. code-block:: yaml

         - uses: actions/checkout@v7
         - uses: actions/checkout@v7
           with:
             repository: inet-framework/inet
             ref: v4.6.0
             path: inet
         - uses: omnetpp/doc-builder@v1
           with:
             ned-path: inet/src
             external-docs: inet=https://inet.omnetpp.org/docs/latest/api/types

``external-docs`` maps NED packages to the documentation of their types; a
type's page is ``<url>/<qualified name>.html``, so the URL above links to the
NED reference of the latest INET release. The pages of message types are named
differently, which ``opp_docgen`` can only know from the tag files of the
dependency's documentation (``msgtags.xml``); INET does not publish them, so the
links to INET's message types do not work.

In the pages of a Sphinx site, ``:ned:`` and ``:msg:`` link only to the
project's own types: the name of a dependency's type renders as code, with a
``neddoc.unknown`` warning (``suppress_warnings = ['neddoc.unknown']`` in
``conf.py`` silences it). Link to the dependency's page with an ordinary link
instead.

Remember to exclude the checkout from your own documentation if it is under
your project directory and you have no ``.nedfolders``, e.g. with
``docgen-args: -x inet``.

The sample model of this site has no dependencies, so its workflow does not do
this.
