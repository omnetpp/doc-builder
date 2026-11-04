"""Marks the PNG images that have a transparent background with the transparent-image class.

Charts, diagrams and screenshots are drawn for a light page, so in the dark scheme they need a light background of
their own (static/omnetpp-immaterial.css). An image counts as transparent if a corner of its first row is: decoding
only that row keeps the check cheap, and needs no image library. An image up to ICON_WIDTH pixels wide (e.g. an icon
in a table) gets the transparent-icon class instead, for a background without padding, which keeps it its size.
"""

import os
import struct
import zlib

from docutils import nodes

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
ICON_WIDTH = 32


def png_chunks(data):
    pos = len(PNG_SIGNATURE)
    while pos + 8 <= len(data):
        length, kind = struct.unpack('>I4s', data[pos:pos + 8])
        yield kind, data[pos + 8:pos + 8 + length]
        pos += 12 + length


def first_row(idat, row_bytes, bpp):
    raw = zlib.decompressobj().decompress(idat, 1 + row_bytes)
    kind, row = raw[0], bytearray(raw[1:1 + row_bytes])
    # The row above the first one is zero, so Up leaves it unchanged, and Paeth is the same as Sub.
    for i in range(bpp, len(row)):
        if kind in (1, 4):
            row[i] = (row[i] + row[i - bpp]) & 0xff
        elif kind == 3:
            row[i] = (row[i] + row[i - bpp] // 2) & 0xff
    return bytes(row)


def has_transparent_corner(width, depth, color, chunks):
    trns = next((body for kind, body in chunks if kind == b'tRNS'), None)
    if color in (0, 2, 3) and trns is None:
        return False
    bits = CHANNELS[color] * depth
    row = first_row(b''.join(body for kind, body in chunks if kind == b'IDAT'), (width * bits + 7) // 8,
                    max(1, bits // 8))
    for x in (0, width - 1):
        if color in (4, 6):
            alpha = row[(x + 1) * bits // 8 - depth // 8]
        elif color == 3:
            index = (row[x * bits // 8] >> (8 - bits - x * bits % 8)) & ((1 << bits) - 1)
            alpha = trns[index] if index < len(trns) else 255
        else:
            continue
        if alpha < 255:
            return True
    return False


def transparent_width(path):
    """The width of the PNG image at path if it has a transparent corner, otherwise None."""
    with open(path, 'rb') as f:
        data = f.read()
    if not data.startswith(PNG_SIGNATURE):
        return None
    try:
        chunks = list(png_chunks(data))
        width, _, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', chunks[0][1])
        if interlace or color not in CHANNELS:
            return None
        return width if has_transparent_corner(width, depth, color, chunks) else None
    except (struct.error, zlib.error, IndexError):
        # A broken image must not fail the build.
        return None


def mark_transparent_images(app, doctree, docname):
    for image in doctree.findall(nodes.image):
        # An image given as name.* is unresolved here; the HTML builder takes its PNG file unless it has an SVG one.
        uri, candidates = image['uri'], image.get('candidates', {})
        if uri.endswith('.*') and 'image/svg+xml' not in candidates:
            uri = candidates.get('image/png', uri)
        path = os.path.join(app.srcdir, uri)
        if not uri.lower().endswith('.png') or not os.path.isfile(path):
            continue
        width = transparent_width(path)
        if width is not None:
            image['classes'].append('transparent-icon' if width <= ICON_WIDTH else 'transparent-image')


def setup(app):
    app.connect('doctree-resolved', mark_transparent_images)
