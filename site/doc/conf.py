project = 'Sample Model'
author = 'OMNeT++ developers'

extensions = [
    'sphinx_immaterial',
    'omnetpp_immaterial',   # the look of the OMNeT++ sites
    'omnetpp_neddoc',       # the :ned: and :msg: roles, linking to the NED reference in ned/
    'omnetpp_doxylink',     # the :cppref: role, linking to the C++ API
]

html_theme = 'sphinx_immaterial'
html_title = project
html_theme_options = {
    'repo_url': 'https://github.com/omnetpp/doc-builder',
}

# The doc-builder action generates the C++ API into api/, with its doxygen tag file
doxylink = {'cppref': ('api/tagfile.xml', 'api/')}

# The PDF is the guide alone: the NED reference and the C++ API are only linked from index.rst.
latex_documents = [('manual', 'sample-model.tex', project, author, 'manual')]
