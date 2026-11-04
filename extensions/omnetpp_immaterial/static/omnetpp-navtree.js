// Renders the navigation trees of the large references of the site (written as JSON by omnetpp_immaterial's navtree)
// under the entry of their root in the sidebar, in the markup of the theme's own nested navigation. The pages carry
// the navigation down to the root only; the children of a group are rendered when the group is first expanded, so a
// page carries a few hundred entries, not thousands. A page listed in several groups (e.g. a type under its package
// and its category) opens in the group whose entry was clicked, so that the navigation keeps its context.
(function () {
  const script = document.currentScript;
  if (!script || !window.omnetppNavJson) return;
  const siteRoot = new URL('../', script.src).href;
  const GROUP = 'omnetpp-navtree.group';
  const roots = window.omnetppNavJson.map(r => ({
    page: new URL(r.page, siteRoot).href,
    dir: new URL(r.dir, siteRoot).href,
    json: new URL(r.json, siteRoot).href,
    tree: null,
  }));
  let counter = 0;

  function strip(url) {
    return url.split(/[?#]/)[0];
  }

  function element(tag, className, attrs) {
    const e = document.createElement(tag);
    if (className) e.className = className;
    for (const [k, v] of Object.entries(attrs || {})) e.setAttribute(k, v);
    return e;
  }

  function label(entry, active) {
    const span = element('span', 'md-ellipsis');
    span.textContent = entry.title;
    if (!entry.href) {
      const div = element('div', 'md-nav__link');
      div.appendChild(span);
      return div;
    }
    const a = element('a', 'md-nav__link' + (active ? ' md-nav__link--active' : ''), {href: entry.href, title: entry.title});
    a.appendChild(span);
    return a;
  }

  function isPage(entry, page) {
    return !!entry.href && !entry.href.includes('#') && strip(entry.href) === page;
  }

  function contains(entry, page) {
    return isPage(entry, page) || (entry.children || []).some(c => contains(c, page));
  }

  function resolve(entries) {
    for (const e of entries) {
      if (e.url) e.href = new URL(e.url, siteRoot).href;
      if (e.children) resolve(e.children);
    }
  }

  function load(root) {
    if (!root.tree) {
      root.tree = fetch(root.json)
        .then(r => r.json())
        .then(t => { resolve(t); return t; });
    }
    return root.tree;
  }

  // Renders a root's tree for one page. The groups are the children of the root; entries outside the group of the
  // context are neither active nor open.
  function renderer(page, rootEntry, groupLevel, context) {
    function item(entry, level, group) {
      const inContext = group === undefined || group === entry;
      const current = inContext && isPage(entry, page);
      if (!entry.children) {
        const li = element('li', 'md-nav__item omnetpp-navtree');
        li.appendChild(label(entry, current));
        return li;
      }
      const open = inContext && (entry.follow !== false || group === entry) && contains(entry, page);
      const id = '__navtree_' + (++counter);
      const li = element('li', 'md-nav__item md-nav__item--nested omnetpp-navtree' + (open ? ' md-nav__item--active' : ''));
      if (level === groupLevel) {
        li.dataset.omnetppNavGroup = entry.title;
        // The menus of the tabs list the groups, but not their pages, too many for a menu.
        li.dataset.omnetppMenu = 'leaf';
      }
      const toggle = element('input', 'md-nav__toggle md-toggle', {type: 'checkbox', id: id});
      toggle.checked = open;
      li.appendChild(toggle);
      const container = element('div', 'md-nav__link md-nav__container');
      container.appendChild(label(entry, current));
      const expander = element('label', 'md-nav__link', {for: id, tabindex: '0'});
      expander.appendChild(element('span', 'md-nav__icon md-icon'));
      container.appendChild(expander);
      li.appendChild(container);
      const nav = element('nav', 'md-nav', {'data-md-level': String(level), 'aria-expanded': String(open)});
      const title = element('label', 'md-nav__title', {for: id});
      title.appendChild(element('span', 'md-nav__icon md-icon'));
      title.appendChild(document.createTextNode(entry.title));
      nav.appendChild(title);
      const list = element('ul', 'md-nav__list', {'data-md-scrollfix': ''});
      nav.appendChild(list);
      li.appendChild(nav);
      const fill = () => {
        if (list.childElementCount) return;
        for (const child of entry.children)
          list.appendChild(item(child, level + 1, entry === rootEntry ? context : undefined));
      };
      if (open) fill();
      toggle.addEventListener('change', () => {
        nav.setAttribute('aria-expanded', String(toggle.checked));
        if (toggle.checked) fill();
      });
      return li;
    }
    return item;
  }

  // The group of the last click in a tree, if it lists the page below its own entry.
  function chooseContext(tree, page) {
    let title = null;
    try { title = sessionStorage.getItem(GROUP); } catch (err) { }
    const group = tree.find(g => g.title === title && (g.children || []).some(c => contains(c, page)));
    if (group) return group;
    return tree.find(g => g.follow !== false && contains(g, page));
  }

  document.addEventListener('click', e => {
    const a = e.target.closest && e.target.closest('li.omnetpp-navtree a.md-nav__link[href]');
    if (!a) return;
    const group = a.closest('li[data-omnetpp-nav-group]');
    try {
      if (group) sessionStorage.setItem(GROUP, group.dataset.omnetppNavGroup);
      else sessionStorage.removeItem(GROUP);
    } catch (err) { }
  }, true);

  function rootItem(primary, rootPage) {
    for (const a of primary.querySelectorAll('a.md-nav__link')) {
      const li = a.closest('li.md-nav__item');
      if (strip(a.href) === rootPage && !li.classList.contains('md-nav__current-toc')) return li;
    }
    return null;
  }

  function activateAncestors(li, primary) {
    let top = li;
    for (let e = li.parentElement; e && e !== primary; e = e.parentElement) {
      if (e.matches('li.md-nav__item')) {
        e.classList.add('md-nav__item--active');
        const toggle = e.querySelector(':scope > input.md-nav__toggle');
        if (toggle) toggle.checked = true;
        top = e;
      }
    }
    const first = top.querySelector('a.md-nav__link[href]');
    if (!first) return;
    for (const tab of document.querySelectorAll('.md-tabs__link')) {
      if (strip(tab.href) === strip(first.href)) tab.closest('.md-tabs__item').classList.add('md-tabs__item--active');
    }
  }

  function render(root, tree, page, primary) {
    const old = rootItem(primary, root.page);
    if (!old) return;
    primary.dataset.omnetppNavtree = 'done';
    const levelNav = old.closest('nav[data-md-level]');
    const level = levelNav ? Number(levelNav.dataset.mdLevel) + 1 : 1;
    const rootLink = old.querySelector('a.md-nav__link');
    const rootEntry = {title: rootLink.textContent.trim(), href: root.page, children: tree};
    const item = renderer(page, rootEntry, level + 1, chooseContext(tree, page));
    const li = item(rootEntry, level);
    old.replaceWith(li);
    activateAncestors(li, primary);
    const active = li.querySelector('.md-nav__link--active');
    const wrap = primary.closest('.md-sidebar__scrollwrap');
    if (active && wrap) {
      const offset = active.getBoundingClientRect().top - wrap.getBoundingClientRect().top;
      wrap.scrollTop += offset - wrap.clientHeight / 3;
    }
  }

  // The first root whose tree lists the page; only the trees of the roots in whose directory the page is are loaded.
  async function update() {
    const page = strip(location.href);
    const primary = document.querySelector('.md-sidebar--primary .md-nav--primary');
    if (!primary || primary.dataset.omnetppNavtree) return;
    for (const root of roots) {
      if (page !== root.page && !page.startsWith(root.dir)) continue;
      const tree = await load(root);
      if (page === root.page || tree.some(e => contains(e, page))) {
        render(root, tree, page, primary);
        return;
      }
    }
  }

  if (window.document$) window.document$.subscribe(update);
  else document.addEventListener('DOMContentLoaded', update);
})();
