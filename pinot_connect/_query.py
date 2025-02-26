from __future__ import annotations

import datetime
import decimal
import json
import typing as t
import uuid
from dataclasses import dataclass
from functools import cached_property

from .exceptions import ProgrammingError


def _escape_single_quotes(value: str) -> str:
    return value.replace("'", "''")


def _escape_param(name_or_index: str | int, value: t.Any):
    if isinstance(value, str):
        return f"'{_escape_single_quotes(value)}'"

    elif isinstance(value, bool):
        return "TRUE" if value else "FALSE"

    elif isinstance(value, (int, float, decimal.Decimal)):
        return str(value)

    elif isinstance(value, (datetime.date, datetime.datetime)):
        return f"'{value.isoformat()}'"

    elif isinstance(value, (list, tuple, set)):
        return f"({', '.join(_escape_param(name_or_index, v) for v in value)})"

    elif value is None:
        return "NULL"

    elif isinstance(value, dict):
        return f"'{_escape_single_quotes(json.dumps(value, separators=(',', ':')))}'"

    elif isinstance(value, uuid.UUID):
        return f"'{str(value)}'"

    else:
        params_type = "name" if isinstance(name_or_index, str) else "index"
        raise ProgrammingError(
            f"Unsupported param type at param {params_type}={name_or_index}: {type(value)}.  Only supported values "
            f"are str, int, float, Decimal, bool, date, datetime. A list/tuple/set of any of those types "
            f"(for IN clauses) is also allowed."
        )


@dataclass
class Query:
    operation: str
    params: tuple | dict | list | None = None

    def __post_init__(self):
        if self.params and not isinstance(self.params, (dict, tuple, list)):
            raise ProgrammingError(f"params must be a dict or tuple, got {type(self.params)}")

    @cached_property
    def escaped_params(self) -> tuple | dict | None:
        if not self.params:
            return None

        if isinstance(self.params, dict):
            return {k: _escape_param(k, v) for k, v in self.params.items()}

        return tuple(_escape_param(i, v) for i, v in enumerate(self.params))

    @cached_property
    def operation_with_params(self) -> str:
        return self.operation % self.escaped_params if self.escaped_params else self.operation
