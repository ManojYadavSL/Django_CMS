# -*- coding: utf-8 -*-
#
# django cms documentation build configuration file, created by
# sphinx-quickstart on Tue Sep 15 10:47:03 2009.
#
# This file is execfile()d with the current directory set to its containing
# dir.
#
# Note that not all possible configuration values are present in this
# autogenerated file.
#
# All configuration values have a default; values that are commented out serve
# to show the default.

import os
import sys

# If extensions (or modules to document with autodoc) are in another
# directory, add these directories to sys.path here. If the directory is
# relative to the documentation root, use os.path.abspath to make it absolute,
# like shown here.

sys.path.append(os.path.abspath('.'))
sys.path.append(os.path.abspath('..'))
sys.path.append(os.path.join(os.path.abspath('.'), '_ext'))

# -- General configuration -----------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
#extensions = ['sphinx.ext.autodoc']

extensions = ['djangocms', 'sphinx.ext.intersphinx', 'sphinx.ext.todo', 'sphinx.ext.autodoc']
intersphinx_mapping = {
    'python': ('http://docs.python.org/3/', None),
    'django': ('https://docs.djangoproject.com/en/1.10/', 'https://docs.djangoproject.com/en/1.10/_objects/'),
    'classytags': ('http://readthedocs.org/docs/django-classy-tags/en/latest/', None),
    'sekizai': ('http://readthedocs.org/docs/django-sekizai/en/latest/', None),
    'treebeard': ('http://django-treebeard.readthedocs.io/en/latest/', None),
}

# Add any paths that contain templates here, relative to this directory.
#templates_path = ['templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The encoding of source files.
source_encoding = 'utf-8'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = u'django cms'
copyright = u'2009-2017, Divio AG and contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.

path = os.path.split(os.path.dirname(__file__))[0]
path = os.path.split(path)[0]
sys.path.insert(0, path)
import cms

version = cms.__version__
# The full version, including alpha/beta/rc tags.
release = cms.__version__

# The language for content autogenerated by Sphinx. Refer to documentation for
# a list of supported languages.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['build', 'env']

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
#today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directory, that shouldn't be
# searched for source files.
exclude_trees = ['build']

# The reST default role (used for this markup: `text`) to use for all
# documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description unit
# titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
#modindex_common_prefix = []

todo_include_todos = True


# -- Options for HTML output ---------------------------------------------------

# on_rtd is whether we are on readthedocs.org
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    try:
        import sphinx_rtd_theme
        html_theme = 'sphinx_rtd_theme'
        html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    except:
        html_theme = 'default'

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
# html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#html_theme_options = {}

# Add any paths that contain custom themes here, relative to this directory.
#html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
#html_title = None

# A shorter title for the navigation bar.  Default is the same as html_title.
#html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = None

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
#html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to
# template names.
#html_additional_pages = {}

# If false, no module index is generated.
#html_use_modindex = True

# If false, no index is generated.
#html_use_index = True

# If true, the index is split into individual pages for each letter.
#html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'djangocmsdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'a4'

# The font size ('10pt', '11pt' or '12pt').
#latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
    ('index', 'djangocms.tex', u'django cms Documentation',
     u'Divio AG and contributors', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top
# of the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
#latex_use_parts = False

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True

# -- Options for LaTeX output --------------------------------------------------

# Spelling check needs an additional module that is not installed by default.
# Add it only if spelling check is requested so docs can be generated without it.
if 'spelling' in sys.argv:
    extensions.append("sphinxcontrib.spelling")

# Spelling language.
spelling_lang = 'en_GB'

# Location of word list.
spelling_word_list_filename = 'spelling_wordlist'

spelling_ignore_pypi_package_names = True

latex_elements = {
    'preamble': r'''\usepackage{CJKutf8}''',
}

from sphinx.util.texescape import tex_replacements
tex_replacements.append(('✕', r'\(\times\)'))
tex_replacements.append(('日', r'\begin{CJK}{UTF8}{min}日\end{CJK}'))
tex_replacements.append(('本', r'\begin{CJK}{UTF8}{min}本\end{CJK}'))
tex_replacements.append(('語', r'\begin{CJK}{UTF8}{min}語\end{CJK}'))



