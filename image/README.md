# doc-builder container image

`ghcr.io/omnetpp/doc-builder`: a self-contained image with the full toolchain to build the documentation sites of
OMNeT++ (manual, guides, tutorials, articles, the doxygen APIs and the `omnetpp.scave` Python API) and of the
simulation models built on it (INET, Simu5G, ...), as HTML and as PDF: doxygen, graphviz, client-side KaTeX math for
HTML, a version-pinned `pandoc` for the OMNeT++ manual's LaTeX→RST conversion, and the Python Sphinx stack of
[`pyproject.toml`](pyproject.toml) and [`uv.lock`](uv.lock), with the OMNeT++ Sphinx extensions of
[`../extensions`](../extensions).

It also carries the OMNeT++ command-line tools of the VS Code extension
(`@omnetpp/opp-tools`: `opp_docgen`, `opp_lint`, `opp_lsp`, `opp_ide_mcp`, run by
the distribution's `nodejs`), so it can generate NED documentation, e.g.
`opp_docgen --format=rst -o <out> <project>`.

The Python packages are installed with uv into a venv on `PATH`, so a build runs
without uv inside the container (the OMNeT++ docs: `make ... PIPRUN= VENVDEP=`).

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

## The OMNeT++ Sphinx extensions

The `Containerfile` copies the extensions of [`../extensions`](../extensions) into the venv, so a project built in
the image enables them in its `conf.py`: `omnetpp_immaterial` (the look of the OMNeT++ sites, on top of
`sphinx_immaterial`), `omnetpp_neddoc` (the `:ned:` and `:msg:` roles and the diagrams of the NED reference),
`omnetpp_doxylink` (the `:cppref:` role), `omnetpp_lexers` (NED, MSG and ini highlighting) and `omnetpp_media`
(videos and audio). Their settings and use are documented on the website of this repository:
[The Theme](https://omnetpp.org/doc-builder/config/theme.html),
[Navigation](https://omnetpp.org/doc-builder/config/navigation.html) and
[The Extensions](https://omnetpp.org/doc-builder/config/extensions.html).

`omnetpp_immaterial` also patches the script of `sphinx_immaterial` 0.13.9 after the build, fixing two of its bugs:
the site search, which finds nothing with Sphinx 9
([sphinx-immaterial#485](https://github.com/jbms/sphinx-immaterial/issues/485)), and the instant navigation with
links or images in inline SVG (e.g. the diagrams of `omnetpp_neddoc`): it fails on a page that has them, and a click
on such a link loads the whole page.

## Naming and tags

| Reference | Meaning |
|-----------|---------|
| `ghcr.io/omnetpp/doc-builder:latest` | the newest image; what the documentation builds of OMNeT++ and INET pull |
| `ghcr.io/omnetpp/doc-builder:vX.Y.Z` | the image of a release of this repository, which the action of that release runs in |
| `ghcr.io/omnetpp/doc-builder:vX` | the image of the `vX` branch (e.g. `v1`), which `omnetpp/doc-builder@vX` runs in; an image built from another branch is named after it the same way, with `-` for `/` |

The image is `linux/amd64` only — every tool in it is fetched as an x86_64 binary,
so the `Containerfile` and `build.sh` pin the platform explicitly.

## Build locally

`@omnetpp/opp-tools` is not published to npm yet, so the image bundles a locally
built npm tarball, from a checkout of omnetpp-vscode that `vscode` in the root of
this repository links to (it is in omnetpp-dev as `vscode/`):

```bash
ln -s ../omnetpp-dev/vscode vscode          # once
(cd vscode && bun run package:cli)          # -> vscode/build/omnetpp-opp-tools-<ver>.tgz
image/build.sh                              # -> ghcr.io/omnetpp/doc-builder:latest
```

`build.sh` takes the single tarball in `vscode/build/` (set `OPP_TOOLS_TGZ=<path>`
to use another one), stages it as `image/opp-tools.tgz` (gitignored, removed
afterwards) for the `Containerfile` to bind-mount, and records its version and the
vscode commit in the image labels:

```bash
podman inspect -f '{{json .Labels}}' ghcr.io/omnetpp/doc-builder:latest
```

The build context is the root of this repository (`image/` and `extensions/`);
building without `build.sh` requires staging the tarball by hand. `IMAGE=<ref>`
builds under another name, e.g. a test image that `doc-builder.sh --image <ref>` or
the documentation build of OMNeT++ (`IMAGE=<ref> doc/src/build.sh <target>`) can try.

The `Containerfile` installs the toolchain first (TeX Live, doxygen, pandoc, the
Python stack from `uv.lock`, the theme's fonts) and checks the PDF build, then adds
the opp-tools and the extensions, the theme last. A change in `extensions/` or a new
opp-tools tarball therefore reuses the cached toolchain and takes seconds; only a
new `uv.lock`, tool version or base image downloads again.

## Publishing

**Currently from a workstation only** (see below): `doc-builder-image.yml` has no
access to the locally built opp-tools tarball, so it deliberately fails in its
first step until the `Containerfile` fetches a published opp-tools version.

Once it is re-enabled, use `.github/workflows/doc-builder-image.yml`: **Actions →
Build doc-builder image → Run workflow**. It needs no personal access token. It is
manual on purpose — republishing `:latest` changes the toolchain under every
subsequent documentation build — so run it after changing the image, and not
otherwise.

To publish from a workstation instead:

```bash
echo "$GHCR_TOKEN" | podman login ghcr.io -u <your-user> --password-stdin
image/build.sh --push       # pushes :latest, :<branch>, and :vX.Y.Z for a release tag
```

Both publish `:latest`, the name of the branch they run on (`:v1` from `v1`), and
for each release tag `vX.Y.Z` on the commit `:vX.Y.Z`: publish from the `v1` branch
after changing it, and the image of a release from its tagged commit, after tagging
it. With a detached HEAD, as in a jj repository, `build.sh` takes the branches at
HEAD (the bookmarks on `@-`). Both stamp an `org.opencontainers.image.source` label
naming the publishing repository — the workflow from `github.repository`,
`build.sh` from the `origin` remote. That label is what makes GHCR link the package
to the repository.

## Toolchain pins

The versions baked into the image are the `Containerfile`'s build args — that file
is the single source of truth, nothing outside it pins these:

| Build arg | Default | Note |
|-----------|---------|------|
| `PANDOC_VERSION` | 3.10 | drives the OMNeT++ manual's LaTeX→RST conversion; the converter is version-sensitive |
| `DOXYGEN_VERSION` | 1.14.0 | newest release doxysphinx's frozen LibSass scoper can still parse |
| `UV_VERSION` | 0.13.1 | build-time only; installs the Sphinx stack from `uv.lock` |

Override one for a test build with `podman build --build-arg PANDOC_VERSION=…`.

The Python packages are pinned by `uv.lock`: change `pyproject.toml` and run
`uv lock` in `image/` to update them.

TeX Live, ImageMagick and librsvg are Ubuntu packages, fixed by the Ubuntu release
in the `FROM` line rather than by a build arg. The build runs a PDF smoke check (a
copy of the OMNeT++ Simulation Manual's preamble, `smoke/manual-preamble.tex`, and
the tiny Sphinx project in `smoke/pdf/` with GIF and SVG images, with both the
OMNeT++ and Sphinx's default fonts), so a missing LaTeX package fails the image
build instead of a later PDF build. Renew the preamble copy when the manual needs
new LaTeX packages.

Exception: opp-tools is whatever tarball `build.sh` bundled; its version is in the
`org.omnetpp.opp-tools.version` (and `.commit`) image labels.

## Using it

- A model project builds its documentation site with the [action](../README.md), which
  runs in this image.
- OMNeT++ builds its documentation in it (omnetpp-dev `doc/src/build.sh`, its release scripts and `deploy-docs.yml`), and so does
  INET (its `doc/src/build`).
- Any other build can run in it or derive from it, and generate the NED reference with `opp_docgen`
  (`--format=rst` to embed it in a Sphinx site, `html-material`/`html-readthedocs` for a standalone subtree):

```dockerfile
FROM ghcr.io/omnetpp/doc-builder:v1
```
