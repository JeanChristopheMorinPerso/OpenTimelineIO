# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

from . _core_utils import add_method
from .. import _otio


@add_method(_otio.Composition)
def each_child(
        self,
        search_range=None,
        descended_from_type=_otio.Composable,
        shallow_search=False,
):
    """
    Generator that returns each child contained in the composition in
    the order in which it is found.

    .. deprecated:: 0.14.0
        Use :meth:`children_if` instead.

    :param TimeRange search_range: if specified, only children whose range overlaps with
                                   the search range will be yielded.
    :param type descended_from_type: if specified, only children who are a descendent
                                     of the descended_from_type will be yielded.
    :param bool shallow_search: if True, will only search children of self, not
                                and not recurse into children of children.
    """
    for child in self.children_if(descended_from_type, search_range, shallow_search):
        yield child
