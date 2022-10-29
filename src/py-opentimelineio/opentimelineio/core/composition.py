# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
from typing import Generator, Type, Any

from . _core_utils import add_method
from .. import _otio, opentime


@add_method(_otio.Composition)
def __str__(self: _otio.Composition) -> str:
    return "{}({}, {}, {}, {})".format(
        self.__class__.__name__,
        str(self.name),
        str(list(self)),
        str(self.source_range),
        str(self.metadata)
    )


@add_method(_otio.Composition)
def __repr__(self: _otio.Composition) -> str:
    return (
        "otio.{}.{}("
        "name={}, "
        "children={}, "
        "source_range={}, "
        "metadata={}"
        ")".format(
            "core" if self.__class__ is _otio.Composition else "schema",
            self.__class__.__name__,
            repr(self.name),
            repr(list(self)),
            repr(self.source_range),
            repr(self.metadata)
        )
    )


@add_method(_otio.Composition)
def each_child(
        self: _otio.Composition,
        search_range: opentime.TimeRange=None,
        descended_from_type: Type[Any]=_otio.Composable,
        shallow_search: bool=False,
) -> Generator[_otio.SerializableObjectWithMetadata, None, None]:
    """
    Generator that returns each child contained in the composition in
    the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`children_if` instead.

    :param search_range: if specified, only children whose range overlaps with
                                   the search range will be yielded.
    :param type descended_from_type: if specified, only children who are a descendent
                                     of the descended_from_type will be yielded.
    :param bool shallow_search: if True, will only search children of self, not
                                and not recurse into children of children.
    """
    yield from self.children_if(descended_from_type, search_range, shallow_search)
