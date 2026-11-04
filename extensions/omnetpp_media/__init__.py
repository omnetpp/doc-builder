"""Video and audio directives: video (looping) and video_noloop, for a local file or a URL, audio, and youtube and
vimeo, for the id of a video there.

    .. youtube:: KUe_vrWbEJY
       :width: 560
       :height: 315

       The caption.

    .. video:: media/run.mp4
       :width: 640

All take the options width, height and align (left, center or right, the default). A local file is resolved
relative to the document, like an image, and published like a :download: target; a URL, or a path starting with a
slash, is used as it is. HTML embeds the media; the other formats, e.g. a PDF, show the caption instead, with a link to
YouTube or Vimeo.

It is part of the doc-builder image, for every OMNeT++ site: a site enables it by listing 'omnetpp_media' in its
extensions.
"""

import html
import os
import pathlib

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from sphinx import addnodes
from sphinx.util import logging
from sphinx.util.osutil import relative_uri

logger = logging.getLogger(__name__)

SRC_PLACEHOLDER = '{src}'


class media_html(nodes.General, nodes.Element):
    """The HTML markup for a local file, whose URL is known only when the builder writes the page: it depends on where
    the page is, e.g. a directory deeper in a dirhtml build, or the root page in a singlehtml build."""


def align_option(argument):
    return directives.choice(argument, ('left', 'center', 'right'))


class MediaDirective(Directive):
    has_content = True
    required_arguments = 1
    option_spec = {
        'width': directives.unchanged,
        'height': directives.unchanged,
        'align': align_option,
    }
    label = None

    def caption(self):
        return ' '.join(line.strip() for line in self.content).strip()

    def size(self):
        return ''.join(f' {name}="{html.escape(self.options[name])}"' for name in ('width', 'height')
                       if self.options.get(name))

    def align(self):
        return self.options.get('align', 'center')

    def media_url(self, uri):
        """The src attribute value and, for a local file, its download file, which the attribute is a placeholder
        for."""
        if '://' in uri or uri.startswith('/'):
            return html.escape(uri), None
        env = self.state.document.settings.env
        rel_path, path = env.relfn2path(uri, env.docname)
        if not os.path.isfile(path):
            logger.warning('media file not found: %s', uri, location=(env.docname, self.lineno))
            return html.escape(uri), None
        return SRC_PLACEHOLDER, env.dlfiles.add_file(env.docname, pathlib.Path(rel_path))

    def result(self, markup, link=None, download=None):
        """The HTML markup, and for the other formats a paragraph with the caption (and the link)."""
        fallback = nodes.paragraph()
        fallback += nodes.strong(text=self.label)
        caption = self.caption()
        if caption:
            fallback += nodes.Text(' – ' + caption)
        if link:
            fallback += nodes.Text(' ')
            fallback += nodes.reference(link, link, refuri=link)
        only = addnodes.only(expr='not html')
        only += fallback
        if download is None:
            return [nodes.raw('', markup, format='html'), only]
        return [media_html(markup=markup, download=os.fspath(download)), only]


class Video(MediaDirective):
    label = 'Video'
    loop = True

    def run(self):
        src, download = self.media_url(self.arguments[0])
        loop = ' loop' if self.loop else ''
        return self.result(f'<video autoplay{loop} controls onclick="this.paused ? this.play() : this.pause();" '
                           f'src="{src}"{self.size()} class="align-{self.align()}"></video>', download=download)


class VideoNoLoop(Video):
    loop = False


class Audio(MediaDirective):
    label = 'Audio'

    def run(self):
        src, download = self.media_url(self.arguments[0])
        caption = html.escape(self.caption())
        return self.result(f'<audio controls class="align-{self.align()}" src="{src}">Audio – {caption}</audio>',
                           download=download)


class Youtube(MediaDirective):
    label = 'YouTube'

    def run(self):
        video_id = self.arguments[0]
        caption = html.escape(self.caption())
        return self.result(f'<div style="text-align: {self.align()}">'
                           f'<iframe src="https://www.youtube.com/embed/{html.escape(video_id)}"{self.size()} '
                           f'frameborder="0" allowfullscreen class="align-{self.align()}"></iframe>'
                           f'<div class="video-caption"><i>{caption}</i></div></div>',
                           link='https://www.youtube.com/watch?v=' + video_id)


class Vimeo(MediaDirective):
    label = 'Vimeo'

    def run(self):
        video_id = self.arguments[0]
        return self.result(f'<iframe src="https://player.vimeo.com/video/{html.escape(video_id)}"{self.size()} '
                           f'frameborder="0" allowfullscreen class="align-{self.align()}"></iframe>',
                           link='https://vimeo.com/' + video_id)


def resolve_media(app, doctree, docname):
    for node in list(doctree.findall(media_html)):
        if app.builder.format != 'html':
            node.parent.remove(node)
            continue
        src = relative_uri(app.builder.get_target_uri(docname), '_downloads/' + node['download'])
        markup = node['markup'].replace(f'src="{SRC_PLACEHOLDER}"', f'src="{html.escape(src)}"', 1)
        node.replace_self(nodes.raw('', markup, format='html'))


def setup(app):
    app.add_node(media_html)
    app.connect('doctree-resolved', resolve_media)
    app.add_directive('video', Video)
    app.add_directive('video_noloop', VideoNoLoop)
    app.add_directive('video_no_loop', VideoNoLoop)
    app.add_directive('audio', Audio)
    app.add_directive('youtube', Youtube)
    app.add_directive('vimeo', Vimeo)
    return {'parallel_read_safe': True, 'parallel_write_safe': True}
