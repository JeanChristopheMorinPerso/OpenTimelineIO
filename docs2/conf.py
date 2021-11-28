# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import re

import sphinx.application

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join('..', 'build', 'lib.linux-x86_64-3.9')))


# -- Project information -----------------------------------------------------

project = 'OpenTimelineIO'
copyright = '2021, Pixar'
author = 'Pixar'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'furo'

html_theme_options = {
    'sidebar_hide_name': True,
    'light_logo': 'OpenTimelineIO@5xDark.png',
    'dark_logo': 'OpenTimelineIO@5xLight.png'
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Both the class’ and the __init__ method’s docstring are concatenated and inserted.
# Pybind11 generates class signatures on the __init__ method.
autoclass_content = 'both'


def process_signature(
    app: sphinx.application.Sphinx,
    what: str,
    name: str,
    obj: object,
    options: dict[str, str],
    signature: str,
    return_annotation
):
    """This does several things:

    * Removes "self" argument from a signature. Pybind11 adds self to
    method arguments, which is useless.

    * Handles overloaded methods/functions by using the docstrings generated
      by Pybind11. Pybind11 adds the signature of each overload in the first function's
      signature. So the idea is to generate a new signature for each one instead.
    """
    signatures = []
    isClass = what == 'class'

    if signature:
        docstrLines = obj.__doc__ and obj.__doc__.split('\n') or []
        if not docstrLines and isClass:
            docstrLines = obj.__init__.__doc__ and obj.__init__.__doc__.split('\n') or []

        if len(docstrLines) > 1 and docstrLines[1] == 'Overloaded function.':
            # Overloaded function detected. Extract each signature and create a new
            # signature for each of them.
            for line in docstrLines:
                nameToMatch = name.split('.')[-1] if not isClass else '__init__'

                # Maybe get use sphinx.util.inspect.signature_from_str ?
                if match := re.search(f'^\d+\.\s{nameToMatch}(\(.*)', line):
                    signatures.append(match.group(1))
        else:
            signatures.append(signature)

    signature = ''

    # Remove self from signatures.
    for index, sig in enumerate(signatures):
        newsig = re.sub('self\: [a-zA-Z0-9._]+(,\s)?', '', sig)
        signatures[index] = newsig

    signature = '\n'.join(signatures)
    return signature, return_annotation


def setup(app):
    """This method is a hook into the Sphinx builder system and injects the
    apidoc module into it so it runs autodoc before running build.

    If you mess with this, you may not see any effect in a local build, this
    was added to get api documentation building on the ReadTheDocs server.
    """
    # app.connect('autodoc-process-docstring', processDocstring)
    app.connect('autodoc-process-signature', process_signature)
