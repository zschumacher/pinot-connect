from __future__ import annotations

import functools
import typing as t

import orjson

if t.TYPE_CHECKING:
    from pinot_connect._result_set import Column

__all__ = [
    "RowMaker",
    "RowType",
    "RowFactory",
    "tuple_row",
    "list_row",
    "dict_row",
    "kwargs_row",
    "args_row",
    "dict_row_load_json_fields",
]

T = t.TypeVar("T", covariant=True)
RowType = t.TypeVar("RowType", covariant=True)


class RowMaker(t.Protocol[RowType]):
    """Protocol for a function that takes a list of values (a row) returned from the query and returns any RowType
    object"""

    def __call__(self, __row: list) -> RowType:
        ...


class RowFactory(t.Protocol[RowType]):
    """Protocol for a factory method that returns a RowMaker.  The method takes a description (from a cursor) which
    is often useful for building dictionaries for usage or for passing into other objects as kwargs"""

    def __call__(self, __description: list[Column]) -> RowMaker[RowType]:
        ...


def _get_column_names(description: list["Column"]) -> list[str]:
    return [c.name for c in description]


def tuple_row(description: list["Column"]) -> RowMaker[tuple]:
    """RowFactory that returns a tuple constructor to convert lis of values to tuple of values

    Returns: RowMaker[tuple[t.Any, ...]]
    """
    return tuple


def list_row(description: list["Column"]) -> RowMaker[list]:
    """RowFactory that is a noop.  The data is returned as a list directly from the query, so this avoids any additional
    data conversion.  This is not the default as most dbapis return tuple rows, but can easily be used when wanted.
    """
    return lambda x: x


def dict_row(description: list["Column"]) -> RowMaker[dict[str, t.Any]]:
    """RowFactory that uses the description to get the column names and injects it into a row maker that converts
    a row to a dictionary
    """
    names = _get_column_names(description)

    def dict_row_(values: list) -> dict[str, t.Any]:
        return dict(zip(names, values))

    return dict_row_


def dict_row_load_json_fields(*fields: str) -> RowFactory[dict[str, t.Any]]:
    """pinot's query api always returns json fields as strings, with no indication that a field is actually a json field
    one way would be to make an additional request to get the metadata of the schema, however the other way that does
    not involve additional IO is specifying the lists of columns that should be loaded to python dictionaries and using
    orjson to do that as efficiently as possible.  This function takes the field names and for those fields, then calls
    orjson.loads on each of the corresponding values
    """

    def dict_row_(description: list["Column"]) -> RowMaker[dict[str, t.Any]]:
        names = _get_column_names(description)

        def dict_row__(values: list) -> dict[str, t.Any]:
            row = dict(zip(names, values))
            for name in fields:
                row[name] = orjson.loads(row[name])
            return row

        return dict_row__

    return dict_row_


def kwargs_row(obj: t.Callable[..., T] | type[T]) -> RowFactory[T]:
    """RowFactory that uses the description to get the column names and builds a dictionary to be passed as kwargs.
    the kwargs are then passed into the passed function or type/model
    """

    def kwargs_row_(description: list["Column"]) -> RowMaker[T]:
        names = _get_column_names(description)

        def kwargs_row__(values: list) -> T:
            kwargs = dict(zip(names, values))
            return obj(**kwargs)

        return kwargs_row__

    return kwargs_row_


def args_row(obj: t.Callable[..., T] | type[T]) -> RowFactory[T]:
    """Row factory that unpacks the row into positional arguments to the passed function or type/model"""

    def args_row_(description: list["Column"]) -> RowMaker[T]:
        def args_row__(values: list) -> T:
            return obj(*values)

        return args_row__

    return args_row_
