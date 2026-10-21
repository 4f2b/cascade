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

html_theme = 'furo'
html_theme_options = {
    'light_css_variables': {
        'color-brand-primary': '#5865f2',
        'color-brand-content': '#5865f2',
        'color-admonition-background': 'rgba(88,101,242,0.07)',
    },
    'dark_css_variables': {
        'color-brand-primary': '#7289da',
        'color-brand-content': '#7289da',
        'color-admonition-background': 'rgba(114,137,218,0.1)',
    },
    'sidebar_hide_name': False,
    'navigation_with_keys': True,
}

html_title = 'cascade'
html_short_title = 'cascade'
html_show_sphinx = False
html_show_copyright = True

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
