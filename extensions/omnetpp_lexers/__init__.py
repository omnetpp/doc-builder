"""Pygments lexers for the OMNeT++ file formats as Sphinx code-block languages: ned, msg, ini and fp (fingerprint test
output).

It is part of the doc-builder image, for every OMNeT++ site: a site enables it by listing 'omnetpp_lexers' in its
extensions. The NED reference that opp_docgen --format=rst generates has ned and msg code blocks, which Sphinx can only
highlight with it.
"""

from .lexers import NedLexer, MsgLexer, IniLexer, FingerprintLexer


def setup(app):
    app.add_lexer('ned', NedLexer)
    app.add_lexer('msg', MsgLexer)
    app.add_lexer('ini', IniLexer)
    app.add_lexer('fp', FingerprintLexer)
    return {
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
