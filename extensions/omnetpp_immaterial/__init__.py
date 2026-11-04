"""The sphinx_immaterial theme in the density of the former OMNeT++ documentation.

The sidebars show more entries: the entries are closer together, and nested lists are shaded by their depth. The
entries that lead into the parts of the site named by omnetpp_nav_nowrap (e.g. an API reference), and the table
of contents of their pages, scroll the sidebar sideways instead of wrapping. The reader sets the widths of the
primary sidebar and of the content by dragging their edges, for every page of the site and later visits. Table
rows are lower, too.

The tabs open their sections as menus (omnetpp_nav_menus), with submenus down to omnetpp_nav_menu_depth levels, built
from the navigation that the page carries, except the tabs named by omnetpp_nav_no_menu. The tabs named by
omnetpp_nav_dropdown (or all, with True) show no navigation sidebar on wide screens, which gives its width to the
content, and are navigated by their menus.

The table of contents follows the section in view also with the theme's instant navigation, which the theme's own
tracking does not. With omnetpp_homepage set, the logo and the name of the site in the header lead to that URL.
The footer names the commit that the pages were built from (omnetpp_commit), credits the OMNeT++ Discrete Event
Simulator, and links to the privacy policy of the site
(omnetpp_privacy_url) and, with the theme's cookie consent configured, to the consent dialog, which the theme opens
as a card at the bottom of the window, leaving the page usable. With html_baseurl set, every page names its canonical URL,
which the theme has a place for but never fills in.

A build that reads no document still writes the CSS and JavaScript bundles of the theme (see bundle_always). The
site search works with the Sphinx of the image, and the instant navigation with links or images in inline SVG, from
and to the pages that have them (see fix_bundle). A page with a ':no-copy:' field at its top gets no copy buttons on its code blocks.
A page outside every toctree, e.g. a type page of the NED reference, still gets its table of contents (see
add_local_toc). The pages of a large generated reference (e.g. a NED reference or a C++ API) are left out of the
navigation that every page carries, and get it from a tree loaded as JSON instead (see navtree). The images drawn for
a light page are inverted in the dark scheme if they are grayscale SVG, and get a light background otherwise (see
images).

It is part of the doc-builder image, for every OMNeT++ site: a site enables it by listing 'omnetpp_immaterial' in its
extensions, with html_theme = 'sphinx_immaterial'.
"""

import json
import os
import pathlib
import re

import markupsafe
from docutils import nodes
from sphinx.environment.adapters.toctree import TocTree
from sphinx.util import logging

from . import images, navtree

logger = logging.getLogger(__name__)

HERE = os.path.dirname(os.path.abspath(__file__))


def config_inited(app, config):
    config.html_static_path.append(os.path.join(HERE, 'static'))
    config.templates_path.append(os.path.join(HERE, 'templates'))


def builder_inited(app):
    if app.config.omnetpp_nav_nowrap:
        app.add_js_file(None, body=f'window.omnetppNavNowrap = {json.dumps(list(app.config.omnetpp_nav_nowrap))};')
    if app.config.omnetpp_nav_menus:
        menus = {'depth': app.config.omnetpp_nav_menu_depth, 'except': list(app.config.omnetpp_nav_no_menu)}
        app.add_js_file(None, body=f'window.omnetppNavMenus = {json.dumps(menus)};')


def dropdown(app, context):
    """Whether the tab of the page is navigated by its menu only."""
    tabs = app.config.omnetpp_nav_dropdown
    if not tabs or 'nav' not in context:
        return False
    tab = next((entry for entry in context['nav'] if entry.active), None)
    if tab is None:
        return False
    return tabs is True or markupsafe.Markup(tab.title).striptags() in tabs


def page_context(app, pagename, templatename, context, doctree):
    # The footer links to it (templates/partials/copyright.html); a site that links to it itself can tell from this
    # being defined that the theme does.
    context['omnetpp_privacy_url'] = app.config.omnetpp_privacy_url
    context['omnetpp_commit'] = app.config.omnetpp_commit
    # The theme leads the logo to the root document of the build, e.g. the start page of a version.
    if app.config.omnetpp_homepage and 'config' in context:
        context['config'].setdefault('extra', {})['homepage'] = app.config.omnetpp_homepage
    if context.get('pageurl') and 'page' in context:
        context['page'].setdefault('canonical_url', context['pageurl'])
    # The theme's own way of hiding the navigation of a page (hide-navigation), which its instant navigation follows.
    if dropdown(app, context) and 'page' in context:
        hide = context['page'].setdefault('meta', {}).setdefault('hide', [])
        if 'navigation' not in hide:
            hide.append('navigation')


def add_local_toc(app, pagename, templatename, context, doctree):
    """The theme takes the table of contents of a page from the page's entry in the navigation, so a page outside
    every toctree has none, nor one left out of the navigation (see navtree). Generated references keep their pages
    out of the toctrees (e.g. opp_docgen's type pages), because the theme writes the whole navigation into every page
    of the site."""
    page = context.get('page')
    if doctree is None or not isinstance(page, dict) or page.get('toc') or pagename == app.config.root_doc:
        return
    from sphinx_immaterial import nav_adapt
    toc = nav_adapt._get_mkdocs_toc(TocTree(app.env).get_toc_for(pagename, app.builder), app.builder)
    nav_adapt._add_domain_info_to_toc(app, toc, pagename)
    if len(toc) == 1:
        options = app.config.html_theme_options
        if not options.get('toc_title') and options.get('toc_title_is_page_title'):
            context['config']['mdx_configs']['toc']['title'] = (toc[0].icon_html or '') + toc[0].title
        toc = toc[0].children
    page['toc'] = toc


def bundle_always(app):
    """The theme generates its CSS and JavaScript bundles (and the CSS of its admonitions) on env-check-consistency,
    which Sphinx only emits when it has read at least one document. A build into an empty output directory that
    keeps the doctrees and reads nothing, e.g. after only a template has changed, would write every page without
    the stylesheets and scripts of the theme."""
    checked = False

    def consistency_checked(app, env):
        nonlocal checked
        checked = True

    def write_started(app, builder):
        if not checked:
            app.events.emit('env-check-consistency', builder.env)

    app.connect('env-check-consistency', consistency_checked)
    app.connect('write-started', write_started)


def mark_no_copy(app, doctree, docname):
    """The theme mounts a copy button on each code block, forcing a layout of the whole page for every block: on a
    page with thousands of them, e.g. a single-page manual, that freezes the browser for minutes."""
    if 'no-copy' not in app.env.metadata.get(docname, {}):
        return
    for node in doctree.findall(nodes.literal_block):
        node['classes'].append('no-copy')


# The JavaScript bundle of the theme, as sphinx-immaterial 0.13.9 ships it, fixed by fix_bundle. The bundle is
# minified, so each pattern matches around whatever names the minifier gave the variables. Each fix has the pattern
# of the broken code, its replacement, and a mark of the replacement, which tells that the bundle is fixed already.
_BUNDLE_GLOB = 'sphinx_immaterial_theme.*.min.js'
_BUNDLE_FIXES = {
    # Sphinx 9 emits the stopword list in _static/language_data.js as a JavaScript Set; it used to be an array. The
    # search code still probes it with indexOf(), so every query dies with "TypeError: stopwords.indexOf is not a
    # function" and the site search stays empty. Drop this once the theme ships its own fix
    # (https://github.com/jbms/sphinx-immaterial/issues/485).
    'search': (re.compile(r'stopwords\.indexOf\((\w+)\)!==-1'),
               r'(stopwords.has?stopwords.has(\1):stopwords.indexOf(\1)!==-1)',
               'stopwords.has'),
    # The instant navigation makes the relative links and sources of a page absolute by assigning the href or src
    # property of each element to itself. The href of an SVG element (e.g. a link or an image in a diagram inlined
    # by omnetpp_neddoc) is a read-only object, so the assignment throws "Cannot set property href of
    # #<SVGImageElement>": a page with such a diagram does not set up instant navigation, and instant navigation
    # to one fails. Such an element gets the absolute URL as its attribute instead.
    'instant navigation': (re.compile(r'let (\w+)=(\w+)\.getAttribute\((\w+)\);'
                                      r'(if\(\1&&!/\^\(\?:\[a-z\]\+:\)\?\\/\\//i\.test\(\1\)\)\{)'
                                      r'\2\[\3\]=\2\[\3\];break\}'),
                           r'let \1=\2.getAttribute(\3);\4typeof \2[\3]=="string"?\2[\3]=\2[\3]:'
                           r'\2.setAttribute(\3,new URL(\1,\2.baseURI).href);break}',
                           '.baseURI).href'),
    # A click on a link goes through the instant navigation unless the link has a target. The target and the href of
    # an SVG link are objects, so such a link always seems to have a target, and a click on a type in a diagram
    # loads the whole page. Their string values are taken instead.
    'link clicks': (re.compile(r'if\((\w+)\.target\|\|(\w+)\.metaKey\|\|\2\.ctrlKey\)return (\w+);'
                               r'let (\w+)=new URL\(\1\.href\);'
                               r'return \4\.search=\4\.hash="",(\w+)\.has\(`\$\{\4\}`\)\?'
                               r'\(\2\.preventDefault\(\),(\w+)\(new URL\(\1\.href\)\)\):\3'),
                    r'if((\1.target.baseVal??\1.target)||\2.metaKey||\2.ctrlKey)return \3;'
                    r'let \4=new URL(\1.href.baseVal??\1.href,\1.baseURI);'
                    r'return \4.search=\4.hash="",\5.has(`${\4}`)?'
                    r'(\2.preventDefault(),\6(new URL(\1.href.baseVal??\1.href,\1.baseURI))):\3',
                    '.target.baseVal??'),
}


def fix_bundle(app, exception):
    if exception is not None:
        return
    get_theme_config = getattr(app.builder, 'get_theme_config', None)
    if get_theme_config is None or get_theme_config()[0] != 'sphinx_immaterial':
        return
    bundles = sorted((pathlib.Path(app.outdir) / '_static').glob(_BUNDLE_GLOB))
    if len(bundles) != 1:
        logger.warning('theme fixup: expected one %s, found %d, search and instant navigation may be broken',
                       _BUNDLE_GLOB, len(bundles))
        return
    source = patched = bundles[0].read_text(encoding='utf-8')
    for name, (broken, fixed, mark) in _BUNDLE_FIXES.items():
        if mark in patched:
            continue
        patched, count = broken.subn(fixed, patched)
        if count != 1:
            logger.warning('theme fixup: %d matches of the %s code in %s, expected 1, %s may be broken', count, name,
                           bundles[0].name, name)
    if patched != source:
        bundles[0].write_text(patched, encoding='utf-8')


def setup(app):
    app.add_config_value('omnetpp_homepage', None, 'html')
    app.add_config_value('omnetpp_nav_nowrap', [], 'html')
    app.add_config_value('omnetpp_nav_menus', True, 'html')
    app.add_config_value('omnetpp_nav_menu_depth', 3, 'html')
    app.add_config_value('omnetpp_nav_no_menu', [], 'html', types=(list, tuple))
    app.add_config_value('omnetpp_nav_dropdown', False, 'html', types=(bool, list, tuple))
    app.add_config_value('omnetpp_privacy_url', None, 'html')
    app.add_config_value('omnetpp_commit', None, 'html')
    app.connect('config-inited', config_inited)
    app.connect('builder-inited', builder_inited)
    app.connect('html-page-context', page_context, priority=900)
    app.connect('html-page-context', add_local_toc, priority=900)
    app.connect('doctree-resolved', mark_no_copy)
    app.connect('build-finished', fix_bundle)
    bundle_always(app)
    images.setup(app)
    navtree.setup(app)
    app.add_css_file('omnetpp-immaterial.css')
    app.add_js_file('omnetpp-immaterial.js', defer='defer')
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
