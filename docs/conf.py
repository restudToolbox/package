import os
import sys


# Add custom CSS
def setup(app):
    app.add_stylesheet("css/custom.css")


# Set variable so that todos are shown in local build
on_rtd = os.environ.get("READTHEDOCS") == "True"

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "respy"
copyright = "2015-2019, Philipp Eisenhauer"  # noqa: A001
author = "Philipp Eisenhauer"

# The full version, including alpha/beta/rc tags.
release = "2.0.0dev2"
version = ".".join(release.split(".")[:2])

# -- General configuration ------------------------------------------------

master_doc = "index"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.ifconfig",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "nbsphinx",
    "numpydoc",
]

nitpicky = True

autodoc_mock_imports = [
    "chaospy",
    "estimagic",
    "numba",
    "numpy",
    "pandas",
    "pytest",
    "scipy",
    "yaml",
]

extlinks = {
    "ghuser": ("https://github.com/%s", "@"),
    "gh": ("https://github.com/OpenSourceEconomics/respy/pulls/%s", "#"),
}

intersphinx_mapping = {
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "python": ("https://docs.python.org/3.6", None),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
html_static_path = ["_static"]

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
language = "en"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "**.ipynb_checkpoints"]

# If true, `todo` and `todoList` produce output, else they produce nothing.
if on_rtd:
    pass
else:
    todo_include_todos = True
    todo_emit_warnings = True

# Configure Sphinx' linkcheck
linkcheck_ignore = [
    r"http://cscubs\.cs\.uni-bonn\.de/*.",
    r"https://(dx\.)?doi\.org/*.",
    r"https://jstor\.org/*.",
    r"https://zenodo\.org/*.",
]

# Configuration for nbsphinx
nbsphinx_execute = "never"
nbsphinx_allow_errors = False

# Configuration for numpydoc
numpydoc_xref_param_type = True
numpydoc_xref_ignore = {"type", "optional", "default"}

# Configuration for autodoc
autosummary_generate = True


# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme_path = ["_themes"]
html_theme = "nature_with_gtoc"
