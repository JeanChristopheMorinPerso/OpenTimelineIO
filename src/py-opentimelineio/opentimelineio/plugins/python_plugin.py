# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Base class for OTIO plugins that are exposed by manifests."""
from __future__ import annotations
import os
import imp
import inspect
import copy
from typing import TYPE_CHECKING, Optional, Union, Any

from .. import (
    core,
    exceptions,
)

from . import (
    manifest
)

if TYPE_CHECKING:
    from types import ModuleType


def plugin_info_map() -> 'dict[str, Union[list[str], dict[Any, Any]]]':
    result: 'dict[str, Union[list[str], dict[Any, Any]]]' = {}
    active_manifest = manifest.ActiveManifest()
    for pt in manifest.OTIO_PLUGIN_TYPES:
        # hooks get handled specially, see below
        if pt == "hooks":
            continue

        type_map = {}
        for plug in getattr(active_manifest, pt):
            try:
                type_map[plug.name] = plug.plugin_info_map()
            except Exception as err:
                type_map[plug.name] = (
                    "ERROR: could not compute plugin_info_map because:"
                    " {}".format(err)
                )

        result[pt] = type_map

    result['hooks'] = copy.deepcopy(active_manifest.hooks)

    result['manifests'] = copy.deepcopy(active_manifest.source_files)

    return result


class PythonPlugin(core.SerializableObject):
    """A class of plugin that is encoded in a python module, exposed via a
    manifest.
    """

    _serializable_label = "PythonPlugin.1"

    def __init__(
        self,
        name: str,
        filepath: str,
    ):
        super().__init__()
        self.name = name
        self.filepath = filepath
        self._json_path: Optional[str] = None
        self._module: Optional['ModuleType'] = None

    name = core.serializable_field("name", required_type=str, doc="Adapter name.")
    filepath = core.serializable_field(
        "filepath",
        str,
        doc=(
            "Absolute path or relative path to adapter module from location of"
            " json."
        )
    )

    def plugin_info_map(self) -> dict[str, Optional[Any]]:
        """Returns a map with information about the plugin."""

        return {
            'name': self.name,
            'doc': inspect.getdoc(self.module()),
            'path': self.module_abs_path(),
            'from manifest': self._json_path
        }

    def module_abs_path(self) -> str:
        """Return an absolute path to the module implementing this adapter."""

        filepath = self.filepath
        if filepath and not os.path.isabs(filepath):
            if not self._json_path:
                raise exceptions.MisconfiguredPluginError(
                    "{} plugin is misconfigured, missing json path. "
                    "plugin: {}".format(
                        self.name,
                        repr(self)
                    )
                )

            filepath = os.path.join(os.path.dirname(self._json_path), filepath)

        return filepath

    def _imported_module(self, namespace: str) -> 'ModuleType':
        """Load the module this plugin points at."""

        pyname = os.path.splitext(os.path.basename(self.module_abs_path()))[0]
        pydir = os.path.dirname(self.module_abs_path())

        (file_obj, pathname, description) = imp.find_module(pyname, [pydir])

        with file_obj:
            # this will reload the module if it has already been loaded.
            mod = imp.load_module(
                f"opentimelineio.{namespace}.{self.name}",
                file_obj,
                pathname,
                description
            )

            return mod

    def module(self) -> 'ModuleType':
        """Return the module object for this adapter. """

        if not self._module:
            self._module = self._imported_module("adapters")

        return self._module

    def _execute_function(self, func_name: str, **kwargs) -> Any:
        """Execute func_name on this adapter with error checking."""

        # collects the error handling into a common place.
        if not hasattr(self.module(), func_name):
            raise exceptions.AdapterDoesntSupportFunctionError(
                f"Sorry, {self.name} doesn't support {func_name}."
            )
        return (getattr(self.module(), func_name)(**kwargs))
