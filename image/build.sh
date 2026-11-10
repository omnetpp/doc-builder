#!/usr/bin/env bash
#
# Build (and optionally publish) the doc-builder image, with the toolchain for both
# the HTML and the PDF documents, as $IMAGE.
#
# Usage:  image/build.sh [--push]
# Env:    IMAGE          image reference (default: ghcr.io/omnetpp/doc-builder:latest)
#         ENGINE         podman (default) or docker
#         OPP_TOOLS_TGZ  a local @omnetpp/opp-tools npm tarball to bundle instead of
#                        the published version of the Containerfile, for a test image
#                        (made in omnetpp-vscode by `bun run package:cli`)
#
# --push publishes $IMAGE, and the image under the name of the branch it is built
# from (:v1 from the v1 branch, which omnetpp/doc-builder@v1 runs in) and of each
# release tag vX.Y.Z on the commit (:vX.Y.Z, which the action of that release runs
# in). The branch is the checked-out one, or, with a detached HEAD (e.g. in a jj
# repository), each branch at HEAD. It refuses to run when the files of the image
# have uncommitted changes, or with OPP_TOOLS_TGZ.
# Log in first:  echo "$GHCR_TOKEN" | podman login ghcr.io -u <user> --password-stdin
#
set -euo pipefail

# Nix shells export SOURCE_DATE_EPOCH (1980-01-01), which podman stamps on the image
# as its creation time: the fresh image then lists as 46 years old, below the layers
# it was built from. The image is not reproducible anyway (apt, downloads).
unset SOURCE_DATE_EPOCH

IMAGE="${IMAGE:-ghcr.io/omnetpp/doc-builder:latest}"
ENGINE="${ENGINE:-podman}"
PUSH=0
[ "${1:-}" = "--push" ] && PUSH=1

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(git -C "$HERE" rev-parse --show-toplevel)"

# GHCR links the package to the repository named by this label, which is what
# lets a workflow's GITHUB_TOKEN pull the image. Derive it from origin so the
# link points at whatever repository actually publishes.
ORIGIN="$(git -C "$REPO" remote get-url origin 2>/dev/null || true)"
case "$ORIGIN" in
    git@github.com:*)     SOURCE="https://github.com/${ORIGIN#git@github.com:}" ;;
    https://github.com/*) SOURCE="$ORIGIN" ;;
    *)                    SOURCE="" ;;
esac
SOURCE="${SOURCE%.git}"

if [ "$PUSH" = "1" ]; then
    uncommitted="$(git -C "$REPO" status --porcelain -- image extensions)"
    if [ -n "$uncommitted" ]; then
        echo "error: --push tags the image with the commit, but its files have uncommitted changes:" >&2
        echo "$uncommitted" >&2
        exit 1
    fi
fi

build_args=()
[ -n "$SOURCE" ] && build_args+=(--label "org.opencontainers.image.source=$SOURCE")

# A local opp-tools tarball is for test images: a published image has the npm
# version that the Containerfile pins, which anyone can rebuild it from.
if [ -n "${OPP_TOOLS_TGZ:-}" ]; then
    if [ "$PUSH" = "1" ]; then
        echo "error: --push publishes the opp-tools version of the Containerfile; unset OPP_TOOLS_TGZ" >&2
        exit 1
    fi
    [ -f "$OPP_TOOLS_TGZ" ] || { echo "error: $OPP_TOOLS_TGZ not found" >&2; exit 1; }
    OPP_TOOLS_VERSION="$(tar -xzOf "$OPP_TOOLS_TGZ" package/package.json \
        | sed -n 's/^ *"version": *"\([^"]*\)".*/\1/p')"
    [ -n "$OPP_TOOLS_VERSION" ] || { echo "error: no version in $OPP_TOOLS_TGZ" >&2; exit 1; }
    tgz_dir="$(dirname "$OPP_TOOLS_TGZ")"
    OPP_TOOLS_COMMIT="$(git -C "$tgz_dir" rev-parse --short HEAD 2>/dev/null || true)"
    if [ -n "$OPP_TOOLS_COMMIT" ] \
        && [ "$(stat -c %Y "$OPP_TOOLS_TGZ")" -lt "$(git -C "$tgz_dir" log -1 --format=%ct)" ]; then
        echo "warning: $OPP_TOOLS_TGZ is older than the HEAD of its repository ($OPP_TOOLS_COMMIT);" \
             "the commit label may not match its contents - rebuild it with bun run package:cli" >&2
    fi

    STAGED="$(mktemp -d)"
    trap 'rm -rf "$STAGED"' EXIT
    cp "$OPP_TOOLS_TGZ" "$STAGED/opp-tools.tgz"
    build_args+=(--build-context "opp-tools-local=$STAGED"
                 --label "org.omnetpp.opp-tools.version=$OPP_TOOLS_VERSION")
    [ -n "$OPP_TOOLS_COMMIT" ] && build_args+=(--label "org.omnetpp.opp-tools.commit=$OPP_TOOLS_COMMIT")
    echo "Bundling opp-tools $OPP_TOOLS_VERSION${OPP_TOOLS_COMMIT:+ (commit $OPP_TOOLS_COMMIT)} from $OPP_TOOLS_TGZ"
fi

echo "Building $IMAGE with $ENGINE (context: $REPO, source: ${SOURCE:-unset})"
"$ENGINE" build --platform linux/amd64 -t "$IMAGE" "${build_args[@]}" -f "$HERE/Containerfile" "$REPO"

if [ "$PUSH" = "1" ]; then
    branches="$(git -C "$REPO" symbolic-ref -q --short HEAD \
        || git -C "$REPO" branch --points-at HEAD --format='%(refname:short)' | grep -v '^(')" || true
    [ -n "$branches" ] || echo "warning: HEAD is on no branch; the image gets no branch tag" >&2
    refs=("$IMAGE")
    # A branch name may have slashes, which an image tag may not
    for name in $branches $(git -C "$REPO" tag --points-at HEAD 'v[0-9]*'); do
        refs+=("${IMAGE%:*}:${name//\//-}")
    done
    echo "Pushing: ${refs[*]}"
    for ref in "${refs[@]}"; do
        [ "$ref" = "$IMAGE" ] || "$ENGINE" tag "$IMAGE" "$ref"
        "$ENGINE" push "$ref"
    done
fi
