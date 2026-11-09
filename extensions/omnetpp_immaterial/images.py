"""Marks the images that are drawn for a light page, for the dark scheme (static/omnetpp-immaterial.css).

A PNG image with a transparent background gets the transparent-image class, for a light background of its own. It
counts as transparent if a corner of its first row is: decoding only that row keeps the check cheap, and needs no
image library. An image up to ICON_WIDTH pixels wide (e.g. an icon in a table) gets the transparent-icon class
instead, for a background without padding, which keeps it its size.

An SVG image in black, white and grays only (e.g. a diagram of modules) gets the adaptive-image class: inverted in the
dark scheme, it is light on the dark page like the text. One with colors or a bitmap in it (e.g. a chart, or the look
of a canvas figure) would show them wrong inverted, so it gets transparent-image, unless it paints a background of its
own. An image that already has one of these classes (e.g. from the :class: option of its figure) is left as it is.

The percent width of an image is of the page, as in a PDF (see omnetpp-immaterial.css): an HTML build limits that of a
bitmap to its real size, which CSS does not know, so that a small image is not enlarged into a blur.
"""

import colorsys
import os
import re
import struct
import xml.etree.ElementTree as ET
import zlib

from docutils import nodes
from sphinx.util.images import get_image_size

PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'
CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}
ICON_WIDTH = 32
CLASSES = ('transparent-image', 'transparent-icon', 'adaptive-image')
# Hue counts from this saturation up: antialiasing and near-grays stay below it.
MIN_SATURATION = 0.25
PAINT_PROPERTIES = ('fill', 'stroke', 'stop-color', 'flood-color', 'lighting-color', 'color')
GRAY_NAMES = {'none', 'transparent', 'currentcolor', 'inherit', 'black', 'white', 'gray', 'grey', 'silver',
              'darkgray', 'darkgrey', 'dimgray', 'dimgrey', 'lightgray', 'lightgrey', 'gainsboro', 'whitesmoke'}
SHAPES = ('rect', 'polygon', 'path', 'circle', 'ellipse', 'line', 'polyline', 'text', 'image', 'use')


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


def is_colored(value):
    value = value.strip().lower()
    if value.startswith('url('):
        return False
    m = re.fullmatch(r'#([0-9a-f]{3}|[0-9a-f]{6})', value)
    if m:
        digits = m.group(1)
        if len(digits) == 3:
            digits = ''.join(c * 2 for c in digits)
        rgb = [int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    else:
        m = re.fullmatch(r'rgba?\(([^)]*)\)', value)
        if not m:
            return value not in GRAY_NAMES
        parts = [p.strip() for p in m.group(1).replace('/', ',').split(',')][:3]
        rgb = [float(p[:-1]) / 100 if p.endswith('%') else float(p) / 255 for p in parts]
    return colorsys.rgb_to_hsv(*rgb)[1] >= MIN_SATURATION


def paints(element):
    """The colors that element paints with, from its attributes and its style."""
    values = [element.get(name) for name in PAINT_PROPERTIES]
    for declaration in (element.get('style') or '').split(';'):
        name, _, value = declaration.partition(':')
        if name.strip() in PAINT_PROPERTIES:
            values.append(value)
    return [v for v in values if v]


def length(value):
    m = re.match(r'\s*([\d.]+)', value or '')
    return float(m.group(1)) if m else None


def paints_background(root, element):
    """Whether element, the first shape that root draws, is an opaque rectangle under all of it."""
    tag = element.tag.rpartition('}')[2]
    fill = element.get('fill', 'black')
    for declaration in (element.get('style') or '').split(';'):
        name, _, value = declaration.partition(':')
        if name.strip() == 'fill':
            fill = value
    if fill.strip().lower() in ('none', 'transparent'):
        return False
    if tag == 'polygon':
        # graphviz draws its background as a polygon around the whole graph
        return True
    if tag != 'rect':
        return False
    box = (root.get('viewBox') or '').replace(',', ' ').split()
    if len(box) == 4:
        width, height = float(box[2]), float(box[3])
    else:
        width, height = length(root.get('width')), length(root.get('height'))
    return bool(width and height and (length(element.get('width')) or 0) >= 0.98 * width
                and (length(element.get('height')) or 0) >= 0.98 * height)


def svg_class(path):
    """The class for the SVG image at path, or None if it needs none or cannot be read."""
    try:
        root = ET.parse(path).getroot()
    except (ET.ParseError, OSError):
        # A broken image must not fail the build.
        return None
    colored = bitmap = False
    first_shape = None
    for element in root.iter():
        tag = element.tag.rpartition('}')[2] if isinstance(element.tag, str) else ''
        if tag == 'image':
            bitmap = True
        if tag == 'style' and element.text:
            colored |= any(is_colored(v) for v in re.findall(r'#[0-9a-fA-F]{3,6}\b|rgba?\([^)]*\)', element.text))
        colored |= any(is_colored(v) for v in paints(element))
        if first_shape is None and tag in SHAPES:
            first_shape = element
    if not colored and not bitmap:
        return 'adaptive-image'
    if first_shape is not None and paints_background(root, first_shape):
        return None
    return 'transparent-image'


def image_uri(image):
    # An image given as name.* is unresolved here; the HTML builder takes its SVG file, else its PNG one.
    uri, candidates = image['uri'], image.get('candidates', {})
    if uri.endswith('.*'):
        uri = candidates.get('image/svg+xml', candidates.get('image/png', uri))
    return uri


def visit_image(self, node):
    uri = image_uri(node)
    percent = node.get('width', '').endswith('%')
    type(self).visit_image(self, node)
    # An SVG image stays sharp at any size.
    if percent and not uri.lower().endswith('.svg'):
        path = os.path.join(self.builder.srcdir, uri)
        size = get_image_size(path) if os.path.isfile(path) else None
        if size:
            self.body[-1] = self.body[-1].replace('style="', f'style="max-width: min(100%, {size[0]}px); ', 1)


def depart_image(self, node):
    type(self).depart_image(self, node)


def mark_transparent_images(app, doctree, docname):
    for image in doctree.findall(nodes.image):
        if any(c in CLASSES for c in image['classes']):
            continue
        uri = image_uri(image)
        path = os.path.join(app.srcdir, uri)
        if not os.path.isfile(path):
            continue
        if uri.lower().endswith('.svg'):
            cls = svg_class(path)
        elif uri.lower().endswith('.png'):
            width = transparent_width(path)
            cls = None if width is None else 'transparent-icon' if width <= ICON_WIDTH else 'transparent-image'
        else:
            continue
        if cls:
            image['classes'].append(cls)


def setup(app):
    app.connect('doctree-resolved', mark_transparent_images)
    app.add_node(nodes.image, override=True, html=(visit_image, depart_image))
