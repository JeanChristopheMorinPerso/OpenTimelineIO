# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.Marker)
def __str__(self: _otio.Marker) -> str:
    return "Marker({}, {}, {})".format(
        str(self.name),
        str(self.marked_range),
        str(self.metadata),
    )


@add_method(_otio.Marker)
def __repr__(self: _otio.Marker) -> str:
    return (
        "otio.schema.Marker("
        "name={}, "
        "marked_range={}, "
        "metadata={}"
        ")".format(
            repr(self.name),
            repr(self.marked_range),
            repr(self.metadata),
        )
    )
