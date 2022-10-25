# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

import importlib.resources

from opentimelineio.plugins import manifest

"""An example plugin package that generates its package manifest on demand.

If you create a plugin that doesn't have a plugin_manifest.json, OTIO will
attempt to call the plugin_manifest() function from the __init__.py directory.

This would allow you to programmatically generate a manifest rather than have
it be static on disk, allowing you to switch features on or off or do some
template substition or any other kind of procedural processing.

This unit test uses a very simple example that just reads the manifest from
a non-standard json file path.
"""


def plugin_manifest():
    return manifest.manifest_from_string(
        importlib.resources.files(__package__).joinpath(
            'unusually_named_plugin_manifest.json'
        ).read_text()
    )
