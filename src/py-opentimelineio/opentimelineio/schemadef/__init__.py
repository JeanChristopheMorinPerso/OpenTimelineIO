# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project
from types import ModuleType


def _add_schemadef_module(name: str, mod: ModuleType) -> None:
    """Insert a new module name and module object into schemadef namespace."""
    ns = globals()  # the namespace dict of the schemadef package
    ns[name] = mod
