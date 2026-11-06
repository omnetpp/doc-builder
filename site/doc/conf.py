import os

project = 'doc-builder'
author = 'OMNeT++ developers'
copyright = '2026, OpenSim Ltd.'

extensions = [
    'sphinx_immaterial',
    'omnetpp_immaterial',   # the look of the OMNeT++ sites
    'omnetpp_neddoc',       # the :ned: and :msg: roles, linking to the NED reference in ned/
    'omnetpp_doxylink',     # the :cppref: role, linking to the C++ API
]

html_theme = 'sphinx_immaterial'
html_title = 'OMNeT++ doc-builder'
html_baseurl = 'https://omnetpp.org/doc-builder/'
html_theme_options = {
    'site_url': html_baseurl,
    'repo_url': 'https://github.com/omnetpp/doc-builder',
    'repo_name': 'omnetpp/doc-builder',
    'icon': {
        'repo': 'fontawesome/brands/github',
        'logo': 'material/book-open-page-variant-outline',
    },
    'globaltoc_collapse': False,
    'toc_title_is_page_title': True,
    'features': [
        'navigation.expand',
        'navigation.instant',
        'navigation.sections',
        'navigation.tabs',
        'navigation.top',
        'search.highlight',
        'toc.follow',
        'toc.sticky',
    ],
    'palette': [
        {
            'media': '(prefers-color-scheme: light)',
            'scheme': 'default',
            'primary': 'indigo',
            'accent': 'deep-orange',
            'toggle': {'icon': 'material/lightbulb-outline', 'name': 'Switch to dark mode'},
        },
        {
            'media': '(prefers-color-scheme: dark)',
            'scheme': 'slate',
            'primary': 'indigo',
            'accent': 'amber',
            'toggle': {'icon': 'material/lightbulb', 'name': 'Switch to light mode'},
        },
    ],
}

# Each tab shows one of the ways the tabs can be navigated (see config/navigation.rst)
omnetpp_nav_no_menu = ['Home']
omnetpp_nav_dropdown = ['Configuration']
omnetpp_nav_nowrap = ['/ned/', '/api/']
# The sample API is too small to reach omnetpp_nav_json_threshold; the tree is what a large API would get
omnetpp_nav_json = ['api/index']

# Untracked files are not counted: the build's own output is among them.
omnetpp_commit = os.popen('git rev-parse --short=10 HEAD').read().strip()
if omnetpp_commit and os.popen('git status --porcelain --untracked-files=no').read():
    omnetpp_commit += '+'
omnetpp_commit = omnetpp_commit or None

# The doc-builder action generates the C++ API into api/, with its doxygen tag file
doxylink = {'cppref': ('api/tagfile.xml', 'api/')}

# The PDF is the guide alone: the NED reference and the C++ API are pages for the web.
latex_documents = [('guide/index', 'doc-builder.tex', 'OMNeT++ doc-builder', author, 'manual')]
