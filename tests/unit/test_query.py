import datetime
import decimal
import uuid

import pytest

from pinot_connect._query import Query
from pinot_connect._query import _escape_param
from pinot_connect.exceptions import ProgrammingError


class TestEscapeFunctions:
    @pytest.mark.parametrize(
        "value, expected",
        [
            ("string", "'string'"),
            ("O'Reilly", "'O''Reilly'"),
            (True, "TRUE"),
            (False, "FALSE"),
            (123, "123"),
            (45.67, "45.67"),
            (decimal.Decimal("12.34"), "12.34"),
            (datetime.date(2024, 1, 1), "'2024-01-01'"),
            (datetime.datetime(2024, 1, 1, 12, 0), "'2024-01-01T12:00:00'"),
            ([1, 2, 3], "(1, 2, 3)"),
            (None, "NULL"),
            ({"key": "value"}, '\'{"key":"value"}\''),
            (uuid.UUID("12345678-1234-5678-1234-567812345678"), "'12345678-1234-5678-1234-567812345678'"),
        ],
    )
    def test_escape_param(self, value, expected):
        assert _escape_param("test", value) == expected

    def test_escape_param_invalid_type(self):
        with pytest.raises(ProgrammingError, match="Unsupported param type at param name=test"):
            _escape_param("test", object())


class TestQuery:
    def test_escaped_params_dict(self):
        query = Query("SELECT * FROM table WHERE name = %(name)s", {"name": "O'Reilly"})
        assert query.escaped_params == {"name": "'O''Reilly'"}

    def test_escaped_params_tuple(self):
        query = Query("SELECT * FROM table WHERE age = %s", (30,))
        assert query.escaped_params == ("30",)

    def test_operation_with_params(self):
        query = Query("SELECT * FROM table WHERE name = %(name)s", {"name": "O'Reilly"})
        assert query.operation_with_params == "SELECT * FROM table WHERE name = 'O''Reilly'"

    def test_no_params(self):
        query = Query("SELECT * FROM table")
        assert query.operation_with_params == "SELECT * FROM table"

    def test_invalid_params(self):
        with pytest.raises(ProgrammingError, match="params must be a dict or tuple, got <class 'set'>"):
            Query("SELECT * FROM table", {1, 2, 3})
