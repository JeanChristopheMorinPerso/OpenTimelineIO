# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from .. core._core_utils import add_method
from .. import _otio


@add_method(_otio.ImageSequenceReference)
def frame_range_for_time_range(self, time_range):
    """Returns first and last frame numbers for
    the given time range in the reference.

    :rtype: tuple[int]
    :raises ValueError: if the provided time range is outside the available range.
    """
    return (
        self.frame_for_time(time_range.start_time),
        self.frame_for_time(time_range.end_time_inclusive())
    )


@add_method(_otio.ImageSequenceReference)
def abstract_target_url(self, symbol):
    """
    Generates a target url for a frame where ``symbol`` is used in place
    of the frame number. This is often used to generate wildcard target urls.
    """
    if not self.target_url_base.endswith("/"):
        base = self.target_url_base + "/"
    else:
        base = self.target_url_base

    return "{}{}{}{}".format(
        base, self.name_prefix, symbol, self.name_suffix
    )
