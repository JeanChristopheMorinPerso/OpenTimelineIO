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
import os
import re
import sys
import inspect
import collections.abc

import sphinx.application

sys.path.insert(0, os.path.abspath(os.path.join("..", "build", "lib.linux-x86_64-3.9")))
# sys.path.insert(0, os.path.abspath(os.path.join('..', 'src', 'py-opentimelineio')))

import opentimelineio

# -- Project information -----------------------------------------------------

project = "OpenTimelineIO"
copyright = "2021, Pixar"
author = "Pixar"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    # 'sphinx.ext.inheritance_diagram',
    "sphinxcontrib.toctree_plus",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

html_theme_options = {
    "sidebar_hide_name": True,
    "light_logo": "OpenTimelineIO@5xDark.png",
    "dark_logo": "OpenTimelineIO@5xLight.png",
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

intersphinx_mapping = {"python": ("https://docs.python.org/3", None)}

# Both the class’ and the __init__ method’s docstring are concatenated and inserted.
# Pybind11 generates class signatures on the __init__ method.
autoclass_content = "both"

add_module_names = False

python_use_unqualified_type_names = True

nitpicky = True


# Renderred enums:
# Fix http://localhost:8000/reference/opentimelineio.core.html#opentimelineio.core.Track.NeighborGapPolicy.never ?
# https://github.com/pybind/pybind11/blob/72282f75a10a5ec9d34d4ab4305546bfbd8d586d/include/pybind11/pybind11.h#L265
# https://github.com/pybind/pybind11/issues/2619
# https://github.com/sphinx-doc/sphinx/pull/7748
# https://github.com/domdfcoding/enum_tools
# https://github.com/pybind/pybind11/issues/2275

# Other issues
# https://github.com/pybind/pybind11/issues/2619 (Generate docstrings that are compatible with Sphinx and stubgen)
# https://github.com/pybind/pybind11/pull/2621 (Rework function signatures in docstrings of overloaded functions)
# https://bugs.python.org/issue39125 (Type signature of @property not shown in help())


# diff --git a/OpenTimelineIO/docs2/asd b/OpenTimelineIO/.venv/lib/python3.9/site-packages/sphinx/ext/autodoc/__init__.py
# index 8fcefcc..037a8ba 100644
# --- a/OpenTimelineIO/docs2/asd
# +++ b/OpenTimelineIO/.venv/lib/python3.9/site-packages/sphinx/ext/autodoc/__init__.py
# @@ -2732,10 +2734,23 @@ class PropertyDocumenter(DocstringStripSignatureMixin, ClassLevelDocumenter):  #
#          else:
#              func = None
#
#          if func and self.config.autodoc_typehints != 'none':
#              try:
#                  signature = inspect.signature(func,
#                                                type_aliases=self.config.autodoc_type_aliases)
# +            except ValueError:
# +                try:
# +                    signature = inspect.signature_from_str(getdoc(func).split('\n')[0])
# +                except ValueError:
# +                    return None
# +
# +            try:
# +
#                  if signature.return_annotation is not Parameter.empty:
#                      objrepr = stringify_typehint(signature.return_annotation)
#                      self.add_line('   :type: ' + objrepr, sourcename)
# @@ -2743,8 +2758,6 @@ class PropertyDocumenter(DocstringStripSignatureMixin, ClassLevelDocumenter):  #
#                  logger.warning(__("Failed to get a function signature for %s: %s"),
#                                 self.fullname, exc)
#                  return None
# -            except ValueError:
# -                return None

# Look at the module code as it extracts signatures from docstrs and removes the signatures from docstrs.
# That's what I need too, but for properties.

# TODO: Map  AnyDictionary to MutableMapping in docs?

# Part of this won't e necessary with https://github.com/pybind/pybind11/pull/2621.
# https://github.com/pybind/pybind11/issues/2619
def process_signature(
    app: sphinx.application.Sphinx,
    what: str,
    name: str,
    obj: object,
    options: dict[str, str],
    signature: str,
    return_annotation,
):
    """This does several things:

    * Removes "self" argument from a signature. Pybind11 adds self to
    method arguments, which is useless.

    * Handles overloaded methods/functions by using the docstrings generated
      by Pybind11. Pybind11 adds the signature of each overload in the first function's
      signature. So the idea is to generate a new signature for each one instead.
    """
    signatures = []
    isClass = what == "class"

    if signature or isClass:
        docstrLines = obj.__doc__ and obj.__doc__.split("\n") or []
        if not docstrLines or isClass:
            # A class can have part of its doc in its docstr or in the __init__ docstr.
            docstrLines += (
                obj.__init__.__doc__ and obj.__init__.__doc__.split("\n") or []
            )

        # This could be solidified by using a regex on the reconstructed docstr?
        if len(docstrLines) > 1 and "Overloaded function." in docstrLines:
            # Overloaded function detected. Extract each signature and create a new
            # signature for each of them.
            for line in docstrLines:
                nameToMatch = name.split(".")[-1] if not isClass else "__init__"

                # Maybe get use sphinx.util.inspect.signature_from_str ?
                if match := re.search(f"^\d+\.\s{nameToMatch}(\(.*)", line):
                    signatures.append(match.group(1))
        elif signature:
            signatures.append(signature)

    signature = ""

    # Remove self from signatures.
    for index, sig in enumerate(signatures):
        newsig = re.sub("self\: [a-zA-Z0-9._]+(,\s)?", "", sig)
        # newsig = re.sub('opentimelineio\._otio\.', '', newsig)
        # newsig = re.sub('opentimelineio\._opentime\.', 'opentimelineio.opentime.', newsig)
        # newsig = re.sub('List\[', 'list[', newsig)

        # References won't be resolved if signatures can't be converted to a real signature.
        # That means signatures like "(item: opentimelineio._otio.Composable, policy: opentimelineio._otio.Track.NeighborGapPolicy = <NeighborGapPolicy.never: 0>)"
        # are invalid. opentimelineio._otio.Composable will never be resolved.
        # This happens in sphinx.domains.python._parse_arglist
        # Check Track.neighbors_of and SerializableCollection.each_child
        # newsig = re.sub('\<([a-zA-Z0-9._]+)\: \d+\>', r'\1', newsig)
        # newsig = re.sub('\<class \'([a-zA-Z0-9._]+)\'>', r'\1', newsig)

        # newsig = newsig.replace('NeighborGapPolicy.never', 'opentimelineio._otio.Track.NeighborGapPolicy')
        signatures[index] = newsig

    # if return_annotation:
    # return_annotation = re.sub('opentimelineio\._otio\.', '', return_annotation)
    # return_annotation = re.sub('opentimelineio\._opentime\.', 'opentimelineio.opentime.', return_annotation)
    # return_annotation = re.sub('List\[', 'list[', return_annotation)

    # if name.endswith('NeighborGapPolicy.name'):
    #     signatures = ['()']
    #     return_annotation = 'str'

    signature = "\n".join(signatures)
    return signature, return_annotation


# def process_bases(
#     app: sphinx.application.Sphinx,
#     name: str,
#     obj: object,
#     options: dict[str, str],
#     bases: list[str]
# ):
#     print(bases)


def process_docstring(
    app: sphinx.application.Sphinx,
    what: str,
    name: str,
    obj: object,
    options: dict[str, str],
    lines: list[str],
):
    # if what == 'class' and f'.. inheritance-diagram:: {name}' not in lines:
    #     lines.append(f'.. inheritance-diagram:: {name}')
    #     lines.append('   :parts: 1')
    #     lines.append('   :top-classes: opentimelineio._otio.SerializableObject')

    for index, line in enumerate(lines):
        if re.match(f'\d+\. {name.split("."[0])}', line):
            line = re.sub("self\: [a-zA-Z0-9._]+(,\s)?", "", line)
            line = re.sub("opentimelineio\._((opentime)|(otio))\.", "", line)
            lines[index] = line


def process_bases(
    app: sphinx.application.Sphinx,
    name: str,
    obj: object,
    options: dict[str, str],
    bases: list[type],
):
    """
    Some classes are Pybind11 binded and are manually registered against
    collection.abc classes.
    """
    klasses = []
    for klass in vars(collections.abc).values():
        if inspect.isclass(klass) and issubclass(obj, klass):
            klasses.append(klass)

    if len(klasses) > 1 and klasses[-1].__module__ == "collections.abc":
        bases.append(klasses[-1])


def setup(app: sphinx.application.Sphinx):
    """This method is a hook into the Sphinx builder system and injects the
    apidoc module into it so it runs autodoc before running build.

    If you mess with this, you may not see any effect in a local build, this
    was added to get api documentation building on the ReadTheDocs server.
    """
    # app.connect('autodoc-process-docstring', processDocstring)
    app.connect("autodoc-process-signature", process_signature)
    # app.connect('autodoc-process-bases', process_bases)
    app.connect("autodoc-process-docstring", process_docstring)
    app.connect("autodoc-process-bases", process_bases)
