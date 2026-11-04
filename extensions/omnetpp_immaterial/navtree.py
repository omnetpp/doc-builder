"""Navigation trees loaded as JSON, for the large generated references of a site (e.g. a NED reference or a C++ API).

The theme writes the whole navigation into every page, so a reference with thousands of pages makes every page of the
site hundreds of kilobytes, and their build quadratic. The documents below a root (a document whose toctree lists more
than omnetpp_nav_json_threshold documents, or one named by omnetpp_nav_json, or one that an extension supplies a tree
for) stay in their toctrees, but not in the navigation that the pages carry: the tree of each root is written once,
to _static/omnetpp-nav/, and omnetpp-navtree.js renders it in the sidebar of the pages below the root, a group of
entries only when it is opened.

An extension supplies the tree of a root by handling the omnetpp-nav-tree event (app, docname), e.g. omnetpp_neddoc
for its reference. Otherwise a root with a doxygen tag file next to it (a C++ API of doxysphinx) gets its classes by
namespace, and its files and topics, and any other root the tree of its toctree. The index document of a directory
with a doxygen tag file is a root of any size, with the pages of the directory that are in no toctree.

An entry of a tree is {'title', 'url', 'children', 'follow'}: the URL is relative to the root of the site, and an
entry with follow False (e.g. a category listing pages that are also listed elsewhere) does not open to the current
page unless it was the one clicked in.
"""

import json
import os
import posixpath
import xml.etree.ElementTree as ElementTree

from sphinx.util.osutil import relative_uri

EVENT = 'omnetpp-nav-tree'
JSON_DIR = 'omnetpp-nav'
# The attribute of the environment where the theme caches its navigation (nav_adapt._get_cached_globaltoc_info).
THEME_CACHE = 'sphinx_immaterial_global_toc_cache'


def title(env, docname):
    return env.titles[docname].astext() if docname in env.titles else docname


def toctree_docs(env, docname):
    """The documents in the toctrees below docname."""
    docs, todo = set(), [docname]
    while todo:
        for child in env.toctree_includes.get(todo.pop(), []):
            if child not in docs and child != docname:
                docs.add(child)
                todo.append(child)
    return docs


def toctree_tree(app, docname, seen=None):
    seen = seen if seen is not None else {docname}
    entries = []
    for child in app.env.toctree_includes.get(docname, []):
        if child in seen or child not in app.env.all_docs:
            continue
        seen.add(child)
        entry = {'title': title(app.env, child), 'url': app.builder.get_target_uri(child)}
        children = toctree_tree(app, child, seen)
        if children:
            entry['children'] = children
        entries.append(entry)
    return entries


def by_name(pages):
    """Leaf entries of (name, docname) pairs, by the last part of the name, or the whole name where that is
    ambiguous."""
    short = lambda name: name.rpartition('::')[2]
    shorts = [short(name) for name, _ in pages]
    return [(short(name) if shorts.count(short(name)) == 1 else name, docname)
            for name, docname in sorted(pages, key=lambda p: (short(p[0]).lower(), p[0]))]


def doxygen_tree(app, docname):
    """The tree of a root whose pages come from doxygen (by doxysphinx), from the tag file next to it: its
    namespaces with their classes, all classes, topics and files; each part only with the pages that the root's
    toctree includes, and for the index of the directory, also those in no toctree (e.g. the class pages of
    doc-builder)."""
    directory = posixpath.dirname(docname)
    path = os.path.join(app.srcdir, directory, 'tagfile.xml')
    if not os.path.isfile(path):
        return None
    docs = toctree_docs(app.env, docname)
    if posixpath.basename(docname) == 'index':
        included = set().union(*app.env.toctree_includes.values())
        docs |= {d for d in app.env.found_docs if posixpath.dirname(d) == directory and d not in included}
    uri = app.builder.get_target_uri
    namespaces, classes, topics, files = {}, [], [], []
    for compound in ElementTree.parse(path).getroot().findall('compound'):
        page = posixpath.join(directory, os.path.splitext(compound.findtext('filename') or '')[0])
        if page not in docs:
            continue
        kind, name = compound.get('kind'), compound.findtext('name')
        if kind in ('class', 'struct', 'union'):
            classes.append((name, page))
        elif kind == 'namespace':
            namespaces[name] = page
        elif kind == 'group':
            topics.append((compound.findtext('title') or name, page))
        elif kind == 'file':
            files.append((posixpath.join(compound.findtext('path') or '', name).lstrip('/'), page))
    covered = set(namespaces.values()) | {page for _, page in classes + topics + files}
    if not covered:
        return None

    members = {name: [] for name in namespaces}
    for name, page in classes:
        scope = max((n for n in namespaces if name.startswith(n + '::')), key=len, default=None)
        if scope is not None:
            members[scope].append((name[len(scope) + 2:], page))
    groups = []
    if namespaces:
        groups.append({'title': 'Namespaces', 'children': [
            {'title': name, 'url': uri(page),
             'children': [{'title': t, 'url': uri(p)} for t, p in by_name(members[name])]}
            for name, page in sorted(namespaces.items(), key=lambda n: n[0].lower())]})
    if classes:
        groups.append({'title': 'Classes', 'follow': False,
                       'children': [{'title': t, 'url': uri(p)} for t, p in by_name(classes)]})
    if topics:
        groups.append({'title': 'Topics', 'children': [{'title': t, 'url': uri(p)}
                                                       for t, p in sorted(topics, key=lambda t: t[0].lower())]})
    if files:
        groups.append({'title': 'Files', 'follow': False,
                       'children': [{'title': t, 'url': uri(p)} for t, p in sorted(files, key=lambda f: f[0].lower())]})
    for group in groups:
        for entry in group['children']:
            if not entry.get('children'):
                entry.pop('children', None)
    # The other pages of the toctree (e.g. the class hierarchy) come first.
    others = [{'title': title(app.env, d), 'url': uri(d)} for d in app.env.toctree_includes.get(docname, [])
              if d not in covered and d in app.env.all_docs]
    if len(groups) == 1:
        groups = groups[0]['children']
    return others + groups


def tree_urls(entries):
    for entry in entries:
        if entry.get('url'):
            yield entry['url'].partition('#')[0]
        yield from tree_urls(entry.get('children', []))


def find_roots(app):
    env, config = app.env, app.config
    threshold = config.omnetpp_nav_json_threshold
    roots = {}
    for docname in sorted(set(env.toctree_includes) | set(config.omnetpp_nav_json)):
        if docname == config.root_doc or docname in config.omnetpp_nav_json_exclude or docname not in env.all_docs:
            continue
        tree = app.events.emit_firstresult(EVENT, docname)
        if tree is None and (docname in config.omnetpp_nav_json
                             or threshold and len(env.toctree_includes.get(docname, [])) > threshold):
            tree = doxygen_tree(app, docname) or toctree_tree(app, docname)
        elif tree is None and posixpath.basename(docname) == 'index':
            # The index of a C++ API whose class pages are in no toctree is a root of any size.
            tree = doxygen_tree(app, docname)
        if tree is not None:
            roots[docname] = tree
    # A root in the toctrees below another one is left out of the navigation with it.
    inner = set()
    for docname in roots:
        inner |= toctree_docs(env, docname) & set(roots)
    return {docname: tree for docname, tree in roots.items() if docname not in inner}


def json_path(docname):
    return f'_static/{JSON_DIR}/{docname.replace("/", "__")}.json'


def write_started(app, builder):
    app.omnetpp_nav_roots = {}
    if builder.format != 'html' or builder.name == 'singlehtml' or builder.get_theme_config()[0] != 'sphinx_immaterial':
        return
    app.omnetpp_nav_roots = find_roots(app)
    if not app.omnetpp_nav_roots:
        return
    # The directory of a root, in which the script looks for the pages that its tree lists.
    roots = [{'page': builder.get_target_uri(d), 'dir': posixpath.dirname(d) + '/' if '/' in d else '',
              'json': json_path(d)} for d in app.omnetpp_nav_roots]
    app.add_js_file(None, body=f'window.omnetppNavJson = {json.dumps(roots)};')
    app.add_js_file('omnetpp-navtree.js', defer='defer')


def prune_navigation(app, pagename, templatename, context, doctree):
    """Leaves the documents below the roots out of the navigation that the theme writes into every page, by
    preparing the theme's cache of the navigation before the theme reads it. A page below a root is mapped to a
    child of the root's entry that does not exist, so that the theme opens the navigation to the root's entry
    without a current entry, as for a page outside every toctree."""
    roots = getattr(app, 'omnetpp_nav_roots', None)
    if not roots or getattr(app.env, THEME_CACHE, None) is not None:
        return
    from sphinx_immaterial import nav_adapt
    builder = app.builder
    base = builder.get_target_uri(nav_adapt._FAKE_DOCNAME)
    nav_url = lambda url: relative_uri(base, url)
    members = {}
    for docname, tree in roots.items():
        urls = {builder.get_target_uri(d) for d in toctree_docs(app.env, docname)} | set(tree_urls(tree))
        members[nav_url(builder.get_target_uri(docname))] = {nav_url(u) for u in urls}
    cache = nav_adapt.CachedTocInfo(app)
    root_keys = []

    def sections(entries, url):
        """The sections of the root's own page, without the documents of its toctrees (which may be in a section)."""
        kept = [e for e in entries if e.url and nav_adapt._strip_fragment(e.url) == url]
        for entry in kept:
            entry.children = sections(entry.children, url)
        return kept

    def prune(entries, parent_key):
        for i, entry in enumerate(entries):
            key = parent_key + (i,)
            url = nav_adapt._strip_fragment(entry.url) if entry.url and not entry.caption_only else None
            if url in members:
                entry.children = sections(entry.children, url)
                root_keys.append((key, url))
            else:
                prune(entry.children, key)

    prune(cache.entries, ())
    cache.url_map, cache.global_toc_keys = nav_adapt._build_toc_index(cache.entries)
    for key, url in root_keys:
        for member in members[url] - {url}:
            if not cache.url_map[member]:
                cache.url_map[member].append(key + (-1,))
    setattr(app.env, THEME_CACHE, cache)


def write_trees(app, exception):
    if exception is not None:
        return
    for docname, tree in getattr(app, 'omnetpp_nav_roots', {}).items():
        path = os.path.join(app.outdir, json_path(docname))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(tree, f, separators=(',', ':'))


def setup(app):
    app.add_config_value('omnetpp_nav_json', [], 'html', types=(list, tuple))
    app.add_config_value('omnetpp_nav_json_exclude', [], 'html', types=(list, tuple))
    app.add_config_value('omnetpp_nav_json_threshold', 100, 'html', types=(int, type(None)))
    app.add_event(EVENT)
    app.connect('write-started', write_started)
    # Before the theme's own handler (priority 500), which builds the cache otherwise.
    app.connect('html-page-context', prune_navigation, priority=400)
    app.connect('build-finished', write_trees)
