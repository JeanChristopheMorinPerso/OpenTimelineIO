# SPDX-License-Identifier: Apache-2.0
# Copyright Contributors to the OpenTimelineIO project

"""Core implementation details and wrappers around the C++ library"""
import functools
from typing import Type, Dict, Optional, Callable, TypeVar, Generic, Any
import types


from .. _otio import ( # noqa
    # errors
    CannotComputeAvailableRangeError,

    # classes
    Composable,
    Composition,
    Item,
    MediaReference,
    SerializableObject,
    SerializableObjectWithMetadata,
    Track,

    # functions
    deserialize_json_from_file,
    deserialize_json_from_string,
    flatten_stack,
    install_external_keepalive_monitor,
    instance_from_schema,
    register_serializable_object_type,
    register_upgrade_function,
    register_downgrade_function,
    set_type_record,
    _serialize_json_to_string,
    _serialize_json_to_file,
    type_version_map,
    release_to_schema_version_map,

    AnyDictionary
)

from . _core_utils import ( # noqa
    add_method,
    _value_to_any,
    _add_mutable_mapping_methods,
    _add_mutable_sequence_methods,
)
from . import ( # noqa
    mediaReference,
    composition,
    composable,
    item,
)


__all__ = [
    'Composable',
    'Composition',
    'Item',
    'MediaReference',
    'SerializableObject',
    'SerializableObjectWithMetadata',
    'Track',
    'deserialize_json_from_file',
    'deserialize_json_from_string',
    'flatten_stack',
    'install_external_keepalive_monitor',
    'instance_from_schema',
    'set_type_record',
    'add_method',
    'upgrade_function_for',
    'downgrade_function_from',
    'serializable_field',
    'deprecated_field',
    'serialize_json_to_string',
    'serialize_json_to_file',
    'register_type',
    'type_version_map',
    'release_to_schema_version_map',
]


def serialize_json_to_string(root: SerializableObject, schema_version_targets: Optional[Dict[str, int]]=None, indent: int=4) -> str:
    """Serialize root to a json string.  Optionally downgrade resulting schemas
    to schema_version_targets.

    :param root: root object to serialize
    :param schema_version_targets: optional dictionary mapping
                                   schema name to desired schema
                                   version, for downgrading the
                                   result to be compatible with
                                   older versions of
                                   OpenTimelineIO.
    :param indent: number of spaces for each json indentation level. Use -1
                   for no indentation or newlines.

    :returns: resulting json string
    """
    return _serialize_json_to_string(
        _value_to_any(root),
        schema_version_targets or {},
        indent
    )


def serialize_json_to_file(
        root: SerializableObject,
        filename: str,
        schema_version_targets: Optional[Dict[str, int]]=None,
        indent: int=4
) -> bool:
    """Serialize root to a json file.  Optionally downgrade resulting schemas
    to schema_version_targets.

    :param root: root object to serialize
    :param schema_version_targets: optional dictionary mapping
                                                  schema name to desired schema
                                                  version, for downgrading the
                                                  result to be compatible with
                                                  older versions of
                                                  OpenTimelineIO.
    :param indent: number of spaces for each json indentation level. Use -1
                       for no indentation or newlines.

    :returns: true for success, false for failure
    """
    return _serialize_json_to_file(
        _value_to_any(root),
        filename,
        schema_version_targets or {},
        indent
    )


def register_type(classobj: Type[SerializableObject], schemaname: Optional[str]=None):
    """Decorator for registering a SerializableObject type

    Example:

    .. code-block:: python

        @otio.core.register_type
        class SimpleClass(otio.core.SerializableObject):
          serializable_label = "SimpleClass.2"
          ...

    :param cls: class to register
    :param schemaname: Schema name (default: parse from serializable_label)
    """
    label = classobj._serializable_label
    if schemaname is None:
        schema_name, schema_version = label.split(".", 2)
    else:
        schema_name, schema_version = schemaname, 1

    register_serializable_object_type(classobj, schema_name, int(schema_version))

    orig_init = classobj.__init__

    def __init__(self, *args, **kwargs):
        orig_init(self, *args, **kwargs)
        set_type_record(self, schema_name)

    classobj.__init__ = __init__
    return classobj


def upgrade_function_for(cls: Type[SerializableObject], version_to_upgrade_to: int):
    """
    Decorator for identifying schema class upgrade functions.

    Example:

    .. code-block:: python

        @upgrade_function_for(MyClass, 5)
        def upgrade_to_version_five(data):
            pass

    This will get called to upgrade a schema of MyClass to version 5. MyClass
    must be a class deriving from :class:`~SerializableObject`.

    The upgrade function should take a single argument - the dictionary to
    upgrade, and return a dictionary with the fields upgraded.

    Remember that you don't need to provide an upgrade function for upgrades
    that add or remove fields, only for schema versions that change the field
    names.

    :param cls: class to upgrade
    :param version_to_upgrade_to: the version to upgrade to
    """

    def decorator_func(func):
        @functools.wraps(func)
        def wrapped_update(data):
            modified = func(data)
            data.update(modified)

        register_upgrade_function(
            cls._serializable_label.split(".")[0],
            version_to_upgrade_to,
            wrapped_update
        )

        return func

    return decorator_func


def downgrade_function_from(cls: Type[SerializableObject], version_to_downgrade_from: int):
    """
    Decorator for identifying schema class downgrade functions.

    Example:

    .. code-block:: python

        @downgrade_function_from(MyClass, 5)
        def downgrade_from_five_to_four(data):
            return {"old_attr": data["new_attr"]}

    This will get called to downgrade a schema of MyClass from version 5 to
    version 4. MyClass must be a class deriving from
    :class:`~SerializableObject`.

    The downgrade function should take a single argument - the dictionary to
    downgrade, and return a dictionary with the fields downgraded.

    :param cls: class to downgrade
    :param version_to_downgrade_from: the function downgrading from this
                                          version to (version - 1)
    """

    def decorator_func(func):
        """ Decorator for marking downgrade functions """
        def wrapped_update(data):
            modified = func(data)
            data.clear()
            data.update(modified)

        register_downgrade_function(
            cls._serializable_label.split(".")[0],
            version_to_downgrade_from,
            wrapped_update
        )
        return func

    return decorator_func


def serializable_field(name: str, required_type: Type[Any]=None, doc: str=None) -> property:
    """
    Convenience function for adding attributes to child classes of
    :class:`~SerializableObject` in such a way that they will be serialized/deserialized
    automatically.

    Use it like this:

    .. code-block:: python

        @core.register_type
        class Foo(SerializableObject):
            bar = serializable_field("bar", required_type=int, doc="example")

    This would indicate that class "foo" has a serializable field "bar".  So:

    .. code-block:: python

        f = foo()
        f.bar = "stuff"

        # serialize & deserialize
        otio_json = otio.adapters.from_name("otio")
        f2 = otio_json.read_from_string(otio_json.write_to_string(f))

        # fields should be equal
        f.bar == f2.bar

    Additionally, the "doc" field will become the documentation for the
    property.

    :param name: name of the field to add
    :param required_type: type required for the field
    :param doc: field documentation
    """

    def getter(self):
        return self._dynamic_fields[name]

    def setter(self, val):
        # always allow None values regardless of value of required_type
        if required_type is not None and val is not None and not isinstance(required_type, types.GenericAlias):
            if not isinstance(val, required_type):
                raise TypeError(
                    "attribute '{}' must be an instance of '{}', not: {}".format(
                        name,
                        required_type,
                        type(val)
                    )
                )

        self._dynamic_fields[name] = val

    return property(getter, setter, doc=doc)


_T1 = TypeVar("_T1")


# Taken from https://github.com/python/mypy/issues/8440#issuecomment-592660739
class Property(property, Generic[_T1]):
    """Generic implementation of a property.

    Allows us to provide type annotations on top of builtin properties.
    """

    def __init__(
            self,
            fget: Optional[Callable[[Any], _T1]] = None,
            fset: Optional[Callable[[Any, _T1], None]] = None,
            fdel: Optional[Callable[[Any], None]] = None,
            doc: Optional[str] = None,
    ) -> None:
        super().__init__(fget, fset, fdel, doc)

    def __get__(self, obj: Any, objtype=None) -> _T1:
        return super().__get__(obj, objtype)

    def __set__(self, obj: Any, value: _T1) -> None:
        super().__set__(obj, value)

    def __delete__(self, obj: Any) -> None:
        super().__delete__(obj)


_T2 = TypeVar("_T2")


def serializable_typed_field(name: str, required_type: Type[_T2], doc: str=None) -> Property[_T2]:
    """
    Convenience function for adding attributes to child classes of
    :class:`~SerializableObject` in such a way that they will be serialized/deserialized
    automatically.

    Use it like this:

    .. code-block:: python

        @core.register_type
        class Foo(SerializableObject):
            bar = serializable_field("bar", required_type=int, doc="example")

    This would indicate that class "foo" has a serializable field "bar".  So:

    .. code-block:: python

        f = foo()
        f.bar = "stuff"

        # serialize & deserialize
        otio_json = otio.adapters.from_name("otio")
        f2 = otio_json.read_from_string(otio_json.write_to_string(f))

        # fields should be equal
        f.bar == f2.bar

    Additionally, the "doc" field will become the documentation for the
    property.

    :param name: name of the field to add
    :param required_type: type required for the field
    :param doc: field documentation
    """

    def getter(self) -> _T2:
        return self._dynamic_fields[name]

    def setter(self, val: _T2):
        self._dynamic_fields[name] = val

    return Property(getter, setter, doc=doc)


def deprecated_field() -> property:
    """For marking attributes on a SerializableObject deprecated."""

    def getter(self):
        raise DeprecationWarning

    def setter(self, val):
        raise DeprecationWarning

    return property(getter, setter, doc="Deprecated field, do not use.")
