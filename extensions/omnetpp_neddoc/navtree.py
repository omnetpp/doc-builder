"""The navigation tree of the NED reference, for omnetpp_immaterial's navigation trees loaded as JSON.

Under the index of the reference, the pages of its toctree: the packages and the namespaces with their types, the
categories of types (e.g. modules), each with its types, the files, and the topics of the reference. A type is listed
under its package (or namespace) and its category, but only the packages and namespaces open to its page.
"""

import os
import posixpath
import re
import xml.etree.ElementTree as ElementTree

from docutils import nodes

# The category pages of opp_docgen: the tag file and the kinds of the types each lists (None: all).
CATEGORIES = {
    'networks': ('nedtags.xml', {'network'}),
    'modules': ('nedtags.xml', {'simple', 'compound'}),
    'module-interfaces': ('nedtags.xml', {'moduleinterface'}),
    'channels': ('nedtags.xml', {'channel'}),
    'channel-interfaces': ('nedtags.xml', {'channelinterface'}),
    'message-definitions': ('msgtags.xml', None),
}


def read_compounds(path, neddoc_dir):
    """(name, docname, kind) of the types in a tag file; the kind (e.g. simple, network, packet) is None from an
    opp_docgen that does not record it."""
    if not os.path.isfile(path):
        return []
    return [(c.findtext('name'), posixpath.join(neddoc_dir, os.path.splitext(c.findtext('filename'))[0]),
             c.get('typekind')) for c in ElementTree.parse(path).getroot().iter('compound')]


def groups(app, items, page, prefix):
    uri = app.builder.get_target_uri
    result = []
    for name in sorted(items, key=str.lower):
        anchor = nodes.make_id(f'neddoc-{prefix}-{name or "default"}')
        result.append({'title': name or '(default)', 'url': f'{uri(page)}#{anchor}',
                       'children': [{'title': t, 'url': uri(d)}
                                    for t, d in sorted(items[name], key=lambda i: i[0].lower())]})
    return result


def ned_packages(compounds):
    packages = {}
    for name, docname, _ in compounds:
        package, _, short = name.rpartition('.')
        packages.setdefault(package, []).append((short, docname))
    return packages


def msg_namespaces(compounds):
    namespaces = {}
    for name, docname, _ in compounds:
        # The page has the namespace and the (possibly nested) class name; the name has only the latter.
        stem = posixpath.basename(docname)
        namespace = '::'.join(stem[len('msg-'):].split('--')[:-len(name.split('::'))])
        namespaces.setdefault(namespace, []).append((name, docname))
    return namespaces


def category(app, compounds, kinds):
    """The types of the given kinds, by their short names, or their full names where these are ambiguous."""
    types = [(name.rpartition('.')[2], name, docname) for name, docname, kind in compounds
             if kinds is None or kind in kinds]
    shorts = [short for short, _, _ in types]
    return [{'title': short if shorts.count(short) == 1 else name, 'url': app.builder.get_target_uri(docname)}
            for short, name, docname in sorted(types, key=lambda t: (t[0].lower(), t[1]))]


def file_pages(app, neddoc_dir):
    """The file pages, by the paths in their titles (e.g. "NED File src/inet/...")."""
    env = app.env
    prefix = f'{neddoc_dir}/files/'
    pages = [(re.sub(r'^\w+ File ', '', env.titles[d].astext()) if d in env.titles else d, d)
             for d in env.found_docs if d.startswith(prefix)]
    return [{'title': t, 'url': app.builder.get_target_uri(d)} for t, d in sorted(pages, key=lambda p: p[0].lower())]


def navigation_tree(app, docname):
    neddoc_dir = app.config.neddoc_dir.strip('/')
    if docname != f'{neddoc_dir}/index':
        return None
    src = os.path.join(app.srcdir, neddoc_dir)
    ned = read_compounds(os.path.join(src, 'nedtags.xml'), neddoc_dir)
    msg = read_compounds(os.path.join(src, 'msgtags.xml'), neddoc_dir)
    if not ned and not msg:
        return None
    env = app.env
    trees = {
        f'{neddoc_dir}/packages': groups(app, ned_packages(ned), f'{neddoc_dir}/packages', 'packages'),
        f'{neddoc_dir}/namespaces': groups(app, msg_namespaces(msg), f'{neddoc_dir}/namespaces', 'namespaces'),
        f'{neddoc_dir}/files': file_pages(app, neddoc_dir),
    }
    flat = {f'{neddoc_dir}/files'}
    for name, (tags, kinds) in CATEGORIES.items():
        trees[f'{neddoc_dir}/{name}'] = category(app, ned if tags == 'nedtags.xml' else msg, kinds)
        flat.add(f'{neddoc_dir}/{name}')
    entries = []
    for child in env.toctree_includes.get(docname, []):
        # The opp_docgen of older images lists every type and file page in the toctree, too.
        if child.startswith((f'{neddoc_dir}/types/', f'{neddoc_dir}/files/')) or child not in env.all_docs:
            continue
        entry = {'title': env.titles[child].astext() if child in env.titles else child,
                 'url': app.builder.get_target_uri(child)}
        if trees.get(child):
            entry['children'] = trees[child]
            if child in flat:
                entry['follow'] = False
        entries.append(entry)
    return entries


def builder_inited(app):
    if 'omnetpp_immaterial' in app.extensions:
        app.connect('omnetpp-nav-tree', navigation_tree)
