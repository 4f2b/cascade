import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'cascade'
copyright = '2026, cascade contributors'
author = 'cascade contributors'
release = '0.2.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.viewcode',
]

autodoc_member_order = 'bysource'
autodoc_typehints = 'description'

napoleon_google_docstring = False
napoleon_numpy_docstring = False
napoleon_use_rtype = False
napoleon_use_ivar = True
napoleon_custom_sections = [('Returns', 'returns_section')]

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'aiohttp': ('https://docs.aiohttp.org/en/stable/', None),
}

html_theme = 'sphinx_rtd_theme'
html_theme_options = {
    'logo_only': False,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
}

html_title = 'cascade'
html_short_title = 'cascade'
html_show_sphinx = False
html_show_copyright = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
