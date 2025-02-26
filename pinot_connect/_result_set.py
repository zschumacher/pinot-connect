from __future__ import annotations

import datetime
import decimal
import itertools
import typing as t
from abc import ABC
from abc import abstractmethod
from collections import namedtuple

from .exceptions import *
from .rows import RowFactory
from .rows import RowMaker
from .rows import RowType

_TYPE_MAP: t.Final[dict[str, type]] = {
    # note that json fields are returned as strings always over the API, which is why JSON is omitted here
    "STRING": str,
    "BOOLEAN": bool,
    "INT": int,
    "LONG": int,
    "FLOAT": float,
    "DOUBLE": float,
    "BYTES": bytes,
    "TIMESTAMP": datetime.datetime,
    "BIG_DECIMAL": decimal.Decimal,
}

Column = namedtuple(
    "Column",
    "name type_code display_size internal_size precision scale null_ok",
    defaults=(None, None, None, None, None, None, None),
)


class _BaseResultSet(ABC, t.Generic[RowType]):
    def __init__(
        self,
        data: t.Iterator[list],
        columns: list[str],
        types: list[str],
        rowcount: int | None,
        arraysize: int,
        row_factory: RowFactory[RowType],
    ):
        self._data = data
        self._rowcount = rowcount
        self._arraysize = arraysize
        self._rownumber = 0
        self._columns = columns
        self._types = types
        self._row_factory = row_factory
        self._description = [
            Column(name=name, type_code=_TYPE_MAP.get(type_code)) for name, type_code in zip(self._columns, self._types)
        ]
        self._row_maker: RowMaker[RowType] = self._row_factory(self._description)

    def _transform_row(self, row: list) -> RowType:
        return self._row_maker(row)

    def _transform_many(self, n: int | t.Literal["all"]) -> list[RowType]:
        data = itertools.islice(self._data, n) if isinstance(n, int) else self._data
        row_gen: t.Iterator[RowType] = map(self._transform_row, data)
        return list(row_gen)

    @property
    def description(self) -> list[Column]:
        return self._description

    @property
    def arraysize(self) -> int:
        return self._arraysize

    @arraysize.setter
    def arraysize(self, value: int):
        if not isinstance(value, int):
            raise TypeError(f"arraysize must be an integer, got {type(value)}")
        elif value < 1:
            raise ValueError("arraysize must be positive and greater than 0")
        self._arraysize = value

    @property
    def rowcount(self) -> int | None:
        return self._rowcount

    @property
    def rownumber(self) -> int | None:
        return self._rownumber

    @abstractmethod
    def scroll(self, value: int, *, mode: t.Literal["relative", "absolute"] = "relative") -> None:
        ...

    @abstractmethod
    def fetchone(self) -> RowType | None:
        ...

    @abstractmethod
    def fetchmany(self, size: int | None) -> list[RowType]:
        ...

    @abstractmethod
    def fetchall(self) -> list[RowType]:
        ...


class EmptyResultSet(_BaseResultSet[RowType]):
    def __init__(self, row_factory: RowFactory[RowType], arraysize: int = 1):
        super().__init__(iter([]), columns=[], types=[], rowcount=None, arraysize=arraysize, row_factory=row_factory)

    @property
    def rowcount(self) -> t.Literal[-1]:
        return -1

    @property
    def rownumber(self) -> None:
        return None

    def scroll(self, value: int, *, mode: t.Literal["relative", "absolute"] = "absolute") -> None:
        raise ProgrammingError("Cannot scroll - must execute a query first.")

    def fetchone(self):
        raise ProgrammingError("Cannot fetchone - must execute query first.")

    def fetchmany(self, size):
        raise ProgrammingError("Cannot fetchmany - must execute query first.")

    def fetchall(self):
        raise ProgrammingError("Cannot fetchall - must execute query first.")


class ResultSet(_BaseResultSet[RowType]):
    def _advance(self, rows: int):
        skipped = list(itertools.islice(self._data, rows))
        num_skipped = len(skipped)
        if num_skipped < rows:
            raise IndexError("Cursor is exhausted")
        self._rownumber += num_skipped

    def _scroll_relative(self, value: int):
        if value < 1:
            raise ProgrammingError(f"Cursor can only move forward, got {value}.")

        self._advance(value)

    def _scroll_absolute(self, value: int):
        if value < 0:
            raise ProgrammingError(f"Cursor index cannot be negative, got {value}.")

        if value < self._rownumber:
            raise ProgrammingError(
                f"Cannot move cursor backward: currently at row {self._rownumber}, requested {value}."
            )

        if value == self._rownumber:
            raise ProgrammingError(f"Tried to move cursor to {value}, but cursor is already at {value}.")

        self._advance(value - self._rownumber)

    def scroll(self, value: int, *, mode: t.Literal["relative", "absolute"] = "relative") -> None:
        if mode not in {"relative", "absolute"}:
            raise NotSupportedError(f"Mode must be 'relative' or 'absolute', got {mode}.")

        if mode == "relative":
            self._scroll_relative(value)
        else:
            self._scroll_absolute(value)

    def fetchone(self):
        try:
            row = next(self._data)
            self._rownumber += 1
            return self._transform_row(row)
        except StopIteration:
            return None

    def fetchmany(self, size: int | None):
        if size is None:
            size = self._arraysize

        if size < 1:
            raise ValueError(f"fetchmany() requires a positive size, got {size}.")

        rows = self._transform_many(size)
        self._rownumber += len(rows)
        return rows

    def fetchall(self):
        rows = self._transform_many("all")
        self._rownumber += len(rows)
        return rows

    def make_empty(self) -> EmptyResultSet[RowType]:
        return EmptyResultSet(self._row_factory, self._arraysize)
