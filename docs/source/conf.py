# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import warnings

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

project = "Ryoma"
copyright = "2024, WuHen-Li"
author = "WuHen-Li"
release = "v1.0.0-beta"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "myst_parser",
    "sphinx_copybutton",
    "sphinx_exec_code",
    "sphinx_tabs.tabs",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.githubpages",
    "sphinx.ext.graphviz",
    "sphinx.ext.ifconfig",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
]

myst_enable_extensions = [
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

coverage_show_missing_items = True
exclude_patterns = []
graphviz_output_format = "svg"
html_css_files = ["css/custom.css"]
html_favicon = "modelinfer.png"
html_sidebars = {}
html_static_path = ["_static"]
html_theme = "furo"
language = "en"
mathdef_link_only = True
master_doc = "index"
pygments_style = "default"
source_suffix = [".rst", ".md"]
templates_path = ["_templates"]

html_context = {
    "default_mode": "auto",  # auto: the documentation theme will follow the system default that you have set (light or dark)
}

html_theme_options = {
    "light_logo": "ryoma.png",
    "dark_logo": "ryoma.png",
}

intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": (f"https://docs.python.org/{3.10}/", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/", None),
    "torch": ("https://pytorch.org/docs/stable/", None),
}

sphinx_gallery_conf = {
    "examples_dirs": ["examples"],
    "gallery_dirs": ["auto_examples", "auto_tutorial"],
    "capture_repr": ("_repr_html_", "__repr__"),
    "ignore_repr_types": r"matplotlib.text|matplotlib.axes",
}

warnings.filterwarnings("ignore", category=FutureWarning)
