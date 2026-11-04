"""The NED reference that opp_docgen --format=rst generates into a Sphinx project (neddoc_dir, by default 'ned').

The :ned: and :msg: roles link type names to its pages, e.g. :ned:`Source`, :ned:`sample.Source` or
:ned:`the source <Source>`. The targets come from the nedtags.xml / msgtags.xml tag files that opp_docgen writes next
to the pages; a short name that is ambiguous links to the first type in the tag file. A name that is not in the tag
files is a warning (neddoc.unknown) and renders as a literal, and so is a name whose page is not in the build
(neddoc.missing), e.g. with the tag files of another build but no neddoc_url. Without a reference (no tag files), the
build warns once (neddoc.no_reference) and all names render as literals. A site silences any of them with
suppress_warnings, e.g. a build that documents only some of the types.

The roles can also link to a reference published by another build, e.g. that of another version: neddoc_tags_dir is
where its tag files are, and neddoc_url is the URL of its root, which turns the links into absolute ones.

In HTML, the diagrams of the reference pages are inlined into the pages, so that the types in them link to their
pages as in the HTML output of opp_docgen; as images, their links would lead to the .rst sources. A diagram shrinks
to the width of the page down to 80% of its size; a wider one scrolls sideways.

With omnetpp_immaterial, the sidebar of the reference pages shows the packages, namespaces, categories and files of
the reference with their types, as a navigation tree loaded as JSON (see navtree).

It also sets up omnetpp_lexers, which highlights the ned and msg code blocks of the reference pages.

It is part of the doc-builder image, for every OMNeT++ model: a site enables it by listing 'omnetpp_neddoc' in its
extensions.
"""

import html
import os
import posixpath
import re
import shutil
import xml.etree.ElementTree as ElementTree

from docutils import nodes, utils
from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.nodes import make_refnode, split_explicit_title
from sphinx.util.osutil import relative_uri

from . import navtree

HERE = os.path.dirname(os.path.abspath(__file__))
TAG_FILES = {'ned': 'nedtags.xml', 'msg': 'msgtags.xml'}
MIN_DIAGRAM_SCALE = 0.8

logger = logging.getLogger(__name__)


def read_tags(path, prefix):
    names = {}
    for compound in ElementTree.parse(path).getroot().iter('compound'):
        name = compound.findtext('name')
        docname = posixpath.join(prefix, os.path.splitext(compound.findtext('filename'))[0])
        names.setdefault(name, docname)
        names.setdefault(name.replace('::', '.').rsplit('.', 1)[-1], docname)
    return names


class TypeRoles:
    def __init__(self):
        self.tags = {kind: {} for kind in TAG_FILES}
        self.tag_paths = []
        self.url = None

    def load(self, app):
        neddoc_dir = app.config.neddoc_dir.strip('/')
        tags_dir = os.path.join(app.srcdir, app.config.neddoc_tags_dir or neddoc_dir)
        self.url = app.config.neddoc_url.rstrip('/') if app.config.neddoc_url else None
        for kind, filename in TAG_FILES.items():
            path = os.path.join(tags_dir, filename)
            if os.path.isfile(path):
                self.tags[kind] = read_tags(path, '' if self.url else neddoc_dir)
                self.tag_paths.append(path)
        if not any(self.tags.values()):
            logger.warning('no NED reference in %s (no %s): :ned: and :msg: render as plain literals',
                           tags_dir, ' or '.join(TAG_FILES.values()), type='neddoc', subtype='no_reference')

    def role(self, kind):
        def role(name, rawtext, text, lineno, inliner, options=None, content=None):
            has_explicit_title, title, target = split_explicit_title(utils.unescape(text))
            literal = nodes.literal(rawtext, title, classes=['xref', kind])
            if not any(self.tags.values()):
                return [literal], []
            env = inliner.document.settings.env
            # The links of the document change with the reference, which an incremental build would not see.
            for path in self.tag_paths:
                env.note_dependency(path)
            docname = self.tags[kind].get(target)
            if docname is None:
                logger.warning('unknown %s type: %s', kind.upper(), target, location=(env.docname, lineno),
                               type='neddoc', subtype='unknown')
                return [literal], []
            if self.url:
                return [nodes.reference(rawtext, '', literal, refuri=f'{self.url}/{docname}.html')], []
            # Not a std:doc reference, which would replace the literal with the plain text of a document link.
            ref = addnodes.pending_xref(rawtext, literal, refdomain='', reftype='neddoc', reftarget=docname,
                                        refdoc=env.docname)
            return [ref], []
        return role


def resolve_reference(app, env, node, contnode):
    if node['reftype'] != 'neddoc':
        return None
    if node['reftarget'] not in env.all_docs:
        logger.warning('the page of %s is not in the build: %s', node.astext(), node['reftarget'], location=node,
                       type='neddoc', subtype='missing')
        return contnode
    return make_refnode(app.builder, node['refdoc'], node['reftarget'], None, contnode)


def inline_svg(svg, svg_dir, target_url, alt):
    """Returns the SVG for inlining into a page, with its links (written relative to the SVG, to the .rst sources)
    replaced by target_url(the source path of the target)."""
    def relink(match):
        attr, url = match.groups()
        if re.match(r'[a-zA-Z][a-zA-Z0-9+.-]*:', url) or url.startswith('#'):
            return match.group(0)
        return f'{attr}="{html.escape(target_url(posixpath.normpath(posixpath.join(svg_dir, url))))}"'
    svg = re.sub(r'^\s*<\?xml[^>]*\?>\s*', '', svg)
    svg = re.sub(r'\b((?:xlink:)?href)="([^"]*)"', relink, svg)
    svg = re.sub(r'\s+target="_top"', '', svg)
    # It shrinks to the width of the page, but not below MIN_DIAGRAM_SCALE: a wider one, e.g. the usage diagram of a
    # type used by many others, scrolls sideways instead of becoming unreadable.
    width = re.match(r'<svg\b[^>]*?\swidth="([\d.]+)"', svg)
    if width:
        min_width = f'min-width: {float(width.group(1)) * MIN_DIAGRAM_SCALE:.0f}px'
        tag = re.match(r'<svg\b[^>]*>', svg).group(0)
        if re.search(r'\sstyle="', tag):
            tag_with_style = re.sub(r'(\sstyle=")', rf'\g<1>{min_width}; ', tag, count=1)
        else:
            tag_with_style = tag.replace('<svg', f'<svg style="{min_width}"', 1)
        svg = tag_with_style + svg[len(tag):]
    return svg.replace('<svg', f'<svg role="img" aria-label="{html.escape(alt)}"', 1)


def inline_diagrams(app, doctree, docname):
    builder = app.builder
    if builder.format != 'html' or not docname.startswith(app.config.neddoc_dir.strip('/') + '/'):
        return

    def target_url(path):
        """The URL of a page or a file (an icon) relative to the page, which can be deeper, e.g. in a dirhtml
        build."""
        if path.endswith('.rst'):
            return builder.get_relative_uri(docname, path[:-len('.rst')])
        return relative_uri(builder.get_target_uri(docname), path)

    for image in list(doctree.findall(nodes.image)):
        uri = image['uri']
        if not uri.endswith('.svg'):
            continue
        with open(os.path.join(app.srcdir, uri), encoding='utf-8') as f:
            svg = inline_svg(f.read(), posixpath.dirname(uri), target_url, image.get('alt', ''))
        image.replace_self(nodes.raw('', f'<div class="neddoc-diagram">{svg}</div>', format='html'))


def copy_icons(app, exception):
    """The inlined diagrams may refer to module icons, which no Sphinx directive copies."""
    neddoc_dir = app.config.neddoc_dir.strip('/')
    source = os.path.join(app.srcdir, neddoc_dir, 'icons')
    if exception is None and app.builder.format == 'html' and os.path.isdir(source):
        shutil.copytree(source, os.path.join(app.outdir, neddoc_dir, 'icons'), dirs_exist_ok=True)


def config_inited(app, config):
    config.html_static_path.append(os.path.join(HERE, 'static'))


def add_diagram_style(app, pagename, templatename, context, doctree):
    """Only the pages of the reference have inlined diagrams, so the others are spared the request."""
    if pagename.startswith(app.config.neddoc_dir.strip('/') + '/'):
        app.add_css_file('omnetpp-neddoc.css')


def setup(app):
    app.setup_extension('omnetpp_lexers')
    app.add_config_value('neddoc_dir', 'ned', 'env', types=(str,))
    app.add_config_value('neddoc_tags_dir', None, 'env', types=(str,))
    app.add_config_value('neddoc_url', None, 'env', types=(str,))
    roles = TypeRoles()
    app.connect('config-inited', config_inited)
    app.connect('builder-inited', roles.load)
    app.connect('builder-inited', navtree.builder_inited)
    app.connect('missing-reference', resolve_reference)
    app.connect('doctree-resolved', inline_diagrams)
    app.connect('html-page-context', add_diagram_style)
    app.connect('build-finished', copy_icons)
    for kind in TAG_FILES:
        app.add_role(kind, roles.role(kind))
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
