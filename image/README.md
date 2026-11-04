# doc-builder container image

A self-contained image with the full toolchain to build the OMNeT++ Sphinx
documentation site (manual, guides, tutorials, articles, the doxygen APIs and the
`omnetpp.scave` Python API) as HTML and as PDF: doxygen, graphviz, client-side KaTeX
math for HTML, a version-pinned `pandoc` for the manual LaTeX→RST conversion, and
the Python Sphinx stack from `doc/src/uv.lock`.

It also carries the OMNeT++ command-line tools of the VS Code extension
(`@omnetpp/opp-tools`: `opp_docgen`, `opp_lint`, `opp_lsp`, `opp_ide_mcp`, run by
the distribution's `nodejs`), so it can generate NED documentation, e.g.
`opp_docgen --format=rst -o <out> <project>`.

The Python packages are installed with uv into a venv on `PATH`, so the build runs
without uv inside the container by passing `PIPRUN=` and `VENVDEP=`.

For the PDF documents it has TeX Live (Ubuntu's `texlive-latex-recommended`,
`-latex-extra`, `-fonts-recommended`, `tex-gyre`, `latexmk`), ImageMagick (with its
SVG coder) for `sphinx.ext.imgconverter`, and `rsvg-convert` for the manual's
figures. They add about 0.5 GB; one image is simpler to build, publish and use than
an HTML image and a PDF variant of it.

The web fonts that `sphinx_immaterial` would download at the start of every build
(Roboto and Roboto Mono, its defaults) are cached in the image, in
`/opt/sphinx-immaterial-cache` (`SPHINX_IMMATERIAL_EXTERNAL_RESOURCE_CACHE_DIR`), so
building the documentation needs no network access. A project that sets other
fonts in `html_theme_options` still downloads them, into a cache directory of its
own (the image's is not writable for non-root users).

## The omnetpp_immaterial theme

`omnetpp_immaterial/` is a Sphinx extension on top of `sphinx_immaterial`, the shared look of the OMNeT++ sites
(INET's inet.omnetpp.org first): denser sidebars with resizable widths, a sticky tab bar whose tabs open their
sections as menus, the name of the site next to the logo, and a footer crediting OMNeT++. The `Containerfile`
copies it into the venv, so a project built in the image enables it in its `conf.py`:

```python
html_theme = 'sphinx_immaterial'
extensions = [..., 'sphinx_immaterial', 'omnetpp_immaterial']
```

Its settings, all optional:

| Setting | Default | Meaning |
|---------|---------|---------|
| `omnetpp_homepage` | `None` | URL that the logo and the name of the site in the header lead to |
| `omnetpp_nav_nowrap` | `[]` | URL path parts (e.g. `'/api/'`) whose sidebar entries scroll sideways instead of wrapping |
| `omnetpp_nav_menus` | `True` | the tabs open their sections as menus |
| `omnetpp_nav_menu_depth` | `3` | levels of submenus |
| `omnetpp_nav_no_menu` | `[]` | tab titles that open no menu |
| `omnetpp_nav_dropdown` | `False` | tab titles (or `True` for all) navigated by their menus alone, without the navigation sidebar |
| `omnetpp_privacy_url` | `None` | URL of the privacy policy of the site, linked from the footer |
| `omnetpp_nav_json_threshold` | `100` | a document whose toctree lists more documents gets a navigation tree loaded as JSON (`0` or `None`: none by size) |
| `omnetpp_nav_json` | `[]` | documents that get one regardless of size, e.g. `['api/index']` |
| `omnetpp_nav_json_exclude` | `[]` | documents that never get one |

With the theme's cookie consent configured (`html_theme_options['consent']`), the footer also links to the consent
dialog, so that the reader can change their choice.

A page whose top has a `:no-copy:` field gets no copy buttons on its code blocks: the theme lays out the whole page
for each button, which freezes the browser for minutes on a page with thousands of code blocks (e.g. a single-page
manual or a large generated reference).

A page outside every toctree, or below the root of a navigation tree loaded as JSON (see below), still gets its table
of contents, which the theme takes from the page's entry in the navigation. That is for generated references such as the NED reference of `opp_docgen --format=rst`, whose type and
file pages are in no toctree: the theme writes the whole navigation into every page of the site, which would make
each page carry hundreds of entries.

The large generated references of a site (a NED reference, a C++ API of doxygen and doxysphinx) get their navigation
from a tree loaded as JSON. Their pages stay in their toctrees, but the navigation that every page of the site carries
ends at the root of the reference (the document whose toctree lists them); the tree of the root is written once,
to `_static/omnetpp-nav/`, and a script renders it in the sidebar of the pages below the root, opening a group only
when the reader expands it. Without it, each page of the site would carry an entry for every page of the reference:
hundreds of kilobytes per page, and a build time that grows with the square of the number of pages. The roots are
found without any setting: `omnetpp_neddoc` supplies the tree of its reference (its packages, namespaces and
categories with their types, and its files); a document whose toctree lists more than `omnetpp_nav_json_threshold`
documents (e.g. the `api/index` of the action) gets its doxygen classes by namespace, and its topics and files, when
there is a doxygen `tagfile.xml` next to it, and the tree of its toctree otherwise. A page listed twice (e.g. a type
under its package and its category) opens in the group that the reader clicked it in. Another extension supplies the
tree of a root by handling the `omnetpp-nav-tree` event (see `omnetpp_immaterial/navtree.py`).

Charts, diagrams and screenshots with a transparent background are drawn for a light page, so in the dark scheme a
PNG image whose top left or top right pixel is transparent gets a white, padded background (the `transparent-image`
class); one up to 32 pixels wide, e.g. an icon in a table, gets it without the padding (`transparent-icon`), keeping
its size. The check reads only the first row of the image. SVG images are left as they are.

It also patches the script of `sphinx_immaterial` 0.13.9 after the build, fixing two of its bugs: the site search,
which finds nothing with Sphinx 9 ([sphinx-immaterial#485](https://github.com/jbms/sphinx-immaterial/issues/485)),
and the instant navigation with links or images in inline SVG (e.g. the diagrams of `omnetpp_neddoc`): it fails on a
page that has them, and a click on such a link loads the whole page.

A site restyles it with its own stylesheet; e.g. `--omnetpp-tabs-edge` is the height of a bottom border that the
site gives the tab bar, which stays below the header while the tab bar is away.

## The omnetpp_doxylink extension

`omnetpp_doxylink/` is the Sphinx extension behind the `:cppref:` role of the OMNeT++ site, a fork of
`sphinxcontrib-doxylink`: it defines roles that link C++ symbols to the HTML pages of a doxygen API, looked up in
doxygen's tag file (`GENERATE_TAGFILE`). Unlike the original, it can leave the symbols of external libraries
unlinked without a warning. Like `omnetpp_immaterial`, the `Containerfile` copies it into the venv, so a project built
in the image enables it in its `conf.py`:

```python
extensions = [..., 'omnetpp_doxylink']
doxylink = {'cppref': ('api/tagfile.xml', 'api/')}
```

after which ``:cppref:`omnetpp::cMessage` `` or ``:cppref:`cModule::getParentModule` `` in the text links to the
page of that class or member. A name matches the symbols that end in it; an argument list, if given, selects among
overloads and must match the declaration's, `const` included (``:cppref:`cModule::getParentModule() const` ``).

Its settings:

| Setting | Default | Meaning |
|---------|---------|---------|
| `doxylink` | `{}` | role name → `(tag file, doxygen HTML root)`, optionally with a third element, the doxygen PDF that the LaTeX builder links to instead; the tag file is a path relative to the directory `sphinx-build` runs in, or a URL; the HTML root is relative to the Sphinx source directory, absolute, or a URL |
| `doxylink_external_namespaces` | `[]` | namespaces (e.g. `'std'`) whose symbols are intentionally not in the tag file; references to them render as plain code without an unresolved-reference warning |
| `doxylink_pdf_files` | `{}` | PDF name (the third element above) → URL or path to fetch it from into the LaTeX output |
| `doxylink_parse_error_ignore_regexes` | `[]` | regular expressions matched against the warnings about tag file entries whose argument list cannot be parsed; matching warnings are not shown (the entries are skipped either way) |

## The omnetpp_lexers extension

`omnetpp_lexers/` adds the Pygments lexers of the OMNeT++ file formats to Sphinx as code-block languages: `ned`,
`msg`, `ini` (in place of Pygments' own, also recognizing `include` lines) and `fp` (fingerprint test output).
The NED reference that `opp_docgen --format=rst` generates has `ned` and `msg` code blocks, which Sphinx only warns
about without it (and leaves unhighlighted). The `Containerfile` copies it into the venv, so a project built in the
image enables it in its `conf.py`; it has no settings:

```python
extensions = [..., 'omnetpp_lexers']
```

```rst
.. code-block:: ned

   simple Txc
   {
       gates:
           input in;
           output out;
   }
```

## The omnetpp_media extension

`omnetpp_media/` adds directives that embed videos and audio in HTML: `video` (looping) and `video_noloop` (also
spelled `video_no_loop`) for a local file or a URL, `audio`, and `youtube` and `vimeo` for the id of a video there.
All take the `width`, `height` and `align` (`left`, `center` or `right`, the default) options, and their content is
the caption. A local file is resolved relative to the document, like an image, and is published like a `:download:`
target; a URL, or a path that starts with a slash, is used as it is. The other formats, e.g. a PDF, show the caption
instead, with a link to YouTube or Vimeo.

```python
extensions = [..., 'omnetpp_media']
```

```rst
.. youtube:: KUe_vrWbEJY
   :width: 560
   :height: 315

   Introduction to the Simulation IDE

.. video:: media/run.mp4
   :width: 640
```

## The omnetpp_neddoc extension

`omnetpp_neddoc/` works with the NED reference that `opp_docgen --format=rst -o <project>/ned ...` generates into a
Sphinx project. Its `:ned:` and `:msg:` roles link type names to the pages of the reference, by the full name or the
short one (``:ned:`Source` ``, ``:ned:`sample.Source` ``, ``:ned:`the source <Source>` ``, ``:msg:`Job` ``), from the
`nedtags.xml` and `msgtags.xml` tag files that `opp_docgen` writes next to the pages; an ambiguous short name links
to the first type in the tag file, and a name that is not there is a warning. In HTML, it inlines the diagrams of the
reference pages, so that the types in them link to their pages, and gives them the colour scheme of
`sphinx_immaterial`; a diagram shrinks to the width of the page down to 80% of its size, and a wider one (e.g. the
usage diagram of a type that many others use) scrolls sideways. It also sets up `omnetpp_lexers`, for the `ned` and `msg` code blocks of the reference.

The `index` page of the reference has the overview pages (packages, modules, files, ...) in its toctree; the type and
file pages are reached from their listings, and are `:orphan:`, in no toctree, so that a theme that writes the whole
navigation into every page (`sphinx_immaterial`) does not give each page of the site an entry for each of them. With
`omnetpp_immaterial`, the sidebar of the reference pages shows the reference as a tree loaded as JSON: its packages
and namespaces, the categories of types (modules, channels, ...) and the files, each with its pages.

```python
extensions = [..., 'omnetpp_neddoc']
neddoc_dir = 'ned'          # where opp_docgen wrote the reference, relative to the Sphinx source directory
```

| Setting | Default | Meaning |
|---------|---------|---------|
| `neddoc_dir` | `'ned'` | the directory of the reference in the Sphinx project (the action's `ned-dir`) |
| `neddoc_tags_dir` | `None` | where the tag files are, if not in `neddoc_dir`; relative to the Sphinx source directory, or absolute |
| `neddoc_url` | `None` | URL of the root of a reference published by another build (e.g. another version), which the roles then link to with absolute URLs; its tag files are in `neddoc_tags_dir` |

A name that is not in the tag files is a warning of type `neddoc.unknown`, and one whose page is not in the build (e.g.
the tag files of another build without `neddoc_url`) is a `neddoc.missing`; both render as plain literals. A build
without tag files warns once, with `neddoc.no_reference`, and renders all names as plain literals. A site silences
them with `suppress_warnings`, e.g. a build that documents only some of the types, or one that has no reference of its
own.

The roles link to one reference; types of dependencies (e.g. INET's, in a model built on INET) render as literals
with a warning. The pages that `opp_docgen` generates link to those with its `-l` option.

## Naming and tags

The same references are used by CI and locally:

| Reference | Meaning |
|-----------|---------|
| `ghcr.io/omnetpp/doc-builder:latest` | what `deploy-docs.yml` pulls; moves with each rebuild |
| `ghcr.io/omnetpp/doc-builder:<short-sha>` | immutable; pin a deployment to an exact toolchain by editing the `image:` line |

The image is `linux/amd64` only — every tool in it is fetched as an x86_64 binary,
so the `Containerfile` and `build.sh` pin the platform explicitly.

## Build locally

`@omnetpp/opp-tools` is not published to npm yet, so the image bundles a locally
built npm tarball. Build it first in the omnetpp-vscode checkout (hosted in-tree as
`vscode/`):

```bash
(cd vscode && bun run package:cli)         # -> vscode/build/omnetpp-opp-tools-<ver>.tgz
doc/src/site/doc-builder/build.sh          # -> ghcr.io/omnetpp/doc-builder:latest
```

`build.sh` takes the single tarball in `vscode/build/` (set `OPP_TOOLS_TGZ=<path>`
to use another one), stages it as `doc/src/site/doc-builder/opp-tools.tgz`
(gitignored, removed afterwards) for the `Containerfile` to bind-mount, and records
its version and the vscode commit in the image labels:

```bash
podman inspect -f '{{json .Labels}}' ghcr.io/omnetpp/doc-builder:latest
```

The build context is `doc/src` (it holds `pyproject.toml`/`uv.lock`); building
without `build.sh` requires staging the tarball by hand.

## Build the docs with it

```bash
doc/src/site/doc-builder/run.sh            # builds ci-html -> doc/src/out
VERSION=6.x doc/src/site/doc-builder/run.sh
```

`run.sh` bind-mounts the repository and runs
`make -C doc/src ci-html PIPRUN= VENVDEP=` inside the container.

It takes any make target, e.g. the PDFs:

```bash
doc/src/site/doc-builder/run.sh do-guides-pdf
doc/src/site/doc-builder/run.sh do-manual-pdf
```

They land in `doc/` (`UserGuide.pdf`, `SimulationManual.pdf`, …).

## CI usage

`.github/workflows/deploy-docs.yml` already runs its build job inside this image
(its deploy job is a plain runner — it only calls the Pages API):

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: read
    container:
      image: ghcr.io/omnetpp/doc-builder:latest
      credentials:                    # needed only while the package is private
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: doc/src/site/deploy/build-all.sh _site
      ...
```

`build-version.sh` auto-detects the image's global Sphinx toolchain and runs
`make ci-html` with uv bypassed (`PIPRUN= VENVDEP=`), so no extra configuration
is needed.

## Publishing

**Currently from a workstation only** (see below): `doc-builder-image.yml` has no
access to the locally built opp-tools tarball, so it deliberately fails in its
first step until the `Containerfile` fetches a published opp-tools version.

Once it is re-enabled, use `.github/workflows/doc-builder-image.yml`: **Actions →
Build doc-builder image → Run workflow**. It publishes both the `:latest` and `:<short-sha>` tags and
needs no personal access token. It is manual on purpose — republishing `:latest`
changes the toolchain under every subsequent deploy — so run it after changing the
`Containerfile`, `pyproject.toml` or `uv.lock`, and not otherwise.

To publish from a workstation instead:

```bash
echo "$GHCR_TOKEN" | podman login ghcr.io -u <your-user> --password-stdin
doc/src/site/doc-builder/build.sh --push     # pushes :latest and :<short-sha>
```

Both paths stamp an `org.opencontainers.image.source` label naming the publishing
repository — the workflow from `github.repository`, `build.sh` from the `origin`
remote. That label is what makes GHCR link the package to the repository, which in
turn lets the build job's `GITHUB_TOKEN` pull it while the package is private.

## Toolchain pins

The versions baked into the image are the `Containerfile`'s build args — that file
is the single source of truth, nothing outside it pins these:

| Build arg | Default | Note |
|-----------|---------|------|
| `PANDOC_VERSION` | 3.10 | drives the manual LaTeX→RST conversion; the converter is version-sensitive |
| `DOXYGEN_VERSION` | 1.14.0 | newest release doxysphinx's frozen LibSass scoper can still parse |
| `UV_VERSION` | 0.11.8 | build-time only; installs the Sphinx stack from `uv.lock` |

Override one for a test build with `podman build --build-arg PANDOC_VERSION=…`.

TeX Live, ImageMagick and librsvg are Ubuntu packages, fixed by the Ubuntu release
in the `FROM` line rather than by a build arg. The build runs a PDF smoke check (the Simulation Manual's real preamble, and the tiny Sphinx project in
`pdf-smoke/` with GIF and SVG images, with both the OMNeT++ and Sphinx's default
fonts), so a missing LaTeX package fails the image build instead of a later PDF
build.

Exception: opp-tools is whatever tarball `build.sh` bundled; its version is in the
`org.omnetpp.opp-tools.version` (and `.commit`) image labels.

## Using it as a base image

Model libraries (e.g. INET) can build their documentation site on top of this
image: derive from it, add their own Python/Sphinx requirements, and generate the
NED reference with `opp_docgen` (`--format=rst` or `markdown` to embed it in a
Sphinx site, `html-material`/`html-readthedocs` for a standalone subtree).

```dockerfile
FROM ghcr.io/omnetpp/doc-builder:<short-sha>
```

A workflow in another repository can pull the image while the package is private
only if the package grants that repository read access (package settings →
Manage Actions access).
