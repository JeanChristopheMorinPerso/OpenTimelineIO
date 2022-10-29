# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

r"""
MediaLinker plugins fire after an adapter has read a file in order to
produce :class:`.MediaReference`\s that point at valid, site specific media.

They expose a ``link_media_reference`` function with the signature:

.. py:function:: link_media_reference(in_clip: opentimelineio.schema.Clip) -> opentimelineio.core.MediaReference  # noqa
   :noindex:

   Example link_media_reference function.

To get context information, they can inspect the metadata on the clip and on
the media reference. The :meth:`.Composable.parent` method can be used to find the containing
track if metadata is stored there.
"""
from __future__ import annotations
import os
import inspect
from typing import TYPE_CHECKING, cast, Optional, Union, Any

from . import (
    exceptions,
    plugins,
    core,
)

if TYPE_CHECKING:
    from .schema import Clip
    from .core import MediaReference


class MediaLinkingPolicy:
    """Enum describing different media linker policies"""
    DoNotLinkMedia = "__do_not_link_media"
    ForceDefaultLinker = "__default"


# @TODO: wrap this up in the plugin system somehow?  automatically generate?
def available_media_linker_names() -> list[str]:
    """Return a string list of the available media linker plugins."""

    return [str(adp.name) for adp in plugins.ActiveManifest().media_linkers]


def from_name(name: str) -> Optional['MediaLinker']:
    """Fetch the media linker object by the name of the adapter directly."""

    if name == MediaLinkingPolicy.ForceDefaultLinker or not name:
        name = os.environ.get("OTIO_DEFAULT_MEDIA_LINKER", "")

    if not name:
        return None

    manifest = plugins.ActiveManifest()
    # @TODO: make this handle the enums
    try:
        return cast('MediaLinker', manifest.from_name(
            name,
            kind_list="media_linkers"
        ))
    except exceptions.NotSupportedError:
        raise exceptions.NotSupportedError(
            "media linker not supported: {}, available: {}".format(
                name,
                available_media_linker_names()
            )
        )


def default_media_linker() -> str:
    try:
        return os.environ['OTIO_DEFAULT_MEDIA_LINKER']
    except KeyError:
        raise exceptions.NoDefaultMediaLinkerError(
            "No default Media Linker set in $OTIO_DEFAULT_MEDIA_LINKER"
        )


def linked_media_reference(
    target_clip: 'Clip',
    media_linker_name: str=MediaLinkingPolicy.ForceDefaultLinker,
    media_linker_argument_map: Optional[dict[str, Any]]=None
) -> Union['Clip', 'MediaReference']:
    media_linker = from_name(media_linker_name)

    if not media_linker:
        return target_clip

    # @TODO: connect this argument map up to the function call through to the
    #        real linker
    if not media_linker_argument_map:
        media_linker_argument_map = {}

    return media_linker.link_media_reference(
        target_clip,
        media_linker_argument_map
    )


@core.register_type
class MediaLinker(plugins.PythonPlugin):
    _serializable_label = "MediaLinker.1"

    def __init__(
        self,
        name: str,
        filepath: str,
    ):
        super().__init__(name, filepath)

    def link_media_reference(self, in_clip: Clip, media_linker_argument_map: Optional[dict[str, Any]]=None) -> 'MediaReference':
        media_linker_argument_map = media_linker_argument_map or {}

        return cast('MediaReference', self._execute_function(
            "link_media_reference",
            in_clip=in_clip,
            media_linker_argument_map=media_linker_argument_map or {}
        ))

    def is_default_linker(self) -> bool:
        return os.environ.get("OTIO_DEFAULT_MEDIA_LINKER", "") == self.name

    def plugin_info_map(self) -> dict[str, Optional[Any]]:
        """Adds extra adapter-specific information to call to the parent fn."""

        result = super().plugin_info_map()

        fn_doc = inspect.getdoc(self.module().link_media_reference)
        if fn_doc:
            mod_doc = [result['doc'] or "", ""]
            mod_doc.append(fn_doc)
            result["doc"] = "\n".join(mod_doc)

        if self.is_default_linker():
            result["** CURRENT DEFAULT MEDIA LINKER"] = True

        return result

    def __str__(self) -> str:
        return "MediaLinker({}, {})".format(
            repr(self.name),
            repr(self.filepath)
        )

    def __repr__(self) -> str:
        return (
            "otio.media_linker.MediaLinker("
            "name={}, "
            "filepath={}"
            ")".format(
                repr(self.name),
                repr(self.filepath)
            )
        )
