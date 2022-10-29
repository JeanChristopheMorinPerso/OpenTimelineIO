# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
from typing import Optional

from . _opentime import ( # noqa
    RationalTime,
    TimeRange,
    TimeTransform,
)

__all__ = [
    'RationalTime',
    'TimeRange',
    'TimeTransform',
    'from_frames',
    'from_timecode',
    'from_time_string',
    'from_seconds',
    'to_timecode',
    'to_frames',
    'to_seconds',
    'to_time_string',
    'range_from_start_end_time',
    'range_from_start_end_time_inclusive',
    'duration_from_start_end_time',
    'duration_from_start_end_time_inclusive',
]

from_frames = RationalTime.from_frames
from_timecode = RationalTime.from_timecode
from_time_string = RationalTime.from_time_string
from_seconds = RationalTime.from_seconds

range_from_start_end_time = TimeRange.range_from_start_end_time
range_from_start_end_time_inclusive = TimeRange.range_from_start_end_time_inclusive
duration_from_start_end_time = RationalTime.duration_from_start_end_time
duration_from_start_end_time_inclusive = (
    RationalTime.duration_from_start_end_time_inclusive
)


def to_timecode(rt: RationalTime, rate: Optional[float]=None, drop_frame: Optional[bool]=None) -> str:
    """Convert a :class:`~RationalTime` into a timecode string."""
    return (
        rt.to_timecode()
        if rate is None and drop_frame is None
        else rt.to_timecode(rate, drop_frame)
    )


def to_frames(rt: RationalTime, rate: Optional[float]=None) -> int:
    """Turn a :class:`~RationalTime` into a frame number."""
    return rt.to_frames() if rate is None else rt.to_frames(rate)


def to_seconds(rt: RationalTime) -> float:
    """Convert a :class:`~RationalTime` into float seconds"""
    return rt.to_seconds()


def to_time_string(rt: RationalTime) -> str:
    """
    Convert this timecode to time as used by ffmpeg, formatted as
    ``hh:mm:ss`` where ss is an integer or decimal number.
    """
    return rt.to_time_string()
