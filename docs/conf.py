"""Sphinx configuration for the H3D documentation."""

from importlib.metadata import version as package_version

project = "H3D"
author = "H3D contributors"
release = version = package_version("h3d")

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.doctest",
]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
myst_heading_anchors = 3
exclude_patterns = ["_build", "contributing.md", "documentation_guidelines.md"]
autosummary_generate = False
autodoc_typehints = "description"
napoleon_numpy_docstring = True
napoleon_google_docstring = False
nitpicky = True
html_theme = "sphinx_book_theme"
html_title = "H3D documentation"
html_baseurl = "https://piglabsai.github.io/h3d/"
html_theme_options = {"show_navbar_depth": 2}
html_show_sourcelink = False
