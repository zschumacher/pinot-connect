import pytest

from pinot_connect._result_set import Column
from pinot_connect._result_set import EmptyResultSet
from pinot_connect._result_set import ResultSet
from pinot_connect.exceptions import NotSupportedError
from pinot_connect.exceptions import ProgrammingError


class TestBaseResultSet:
    def test_description(self):
        rs = ResultSet(iter([]), ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        expected_description = [Column(name="id", type_code=int), Column(name="name", type_code=str)]
        assert rs.description == expected_description

    def test_arraysize_setter(self):
        rs = ResultSet(iter([]), [], [], None, 1, row_factory=lambda desc: lambda row: row)
        rs.arraysize = 5
        assert rs.arraysize == 5

        with pytest.raises(TypeError, match="arraysize must be an integer"):
            rs.arraysize = "invalid"

        with pytest.raises(ValueError, match="arraysize must be positive and greater than 0"):
            rs.arraysize = 0

    def test_transform_row(self):
        data = iter([[1, "test"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        assert rs._transform_row([1, "test"]) == [1, "test"]

    def test_transform_many(self):
        data = iter([[1, "test"], [2, "data"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        assert rs._transform_many(2) == [[1, "test"], [2, "data"]]

    def test_rowcount(self):
        rs = ResultSet(iter([]), [], [], 5, 1, row_factory=lambda desc: lambda row: row)
        assert rs.rowcount == 5


class TestEmptyResultSet:
    def test_rowcount(self):
        rs = EmptyResultSet(row_factory=lambda x: x)
        assert rs.rowcount == -1

    def test_rownumber(self):
        rs = EmptyResultSet(row_factory=lambda x: x)
        assert rs.rownumber is None

    def test_scroll_raises_error(self):
        rs = EmptyResultSet(row_factory=lambda x: x)
        with pytest.raises(ProgrammingError, match="Cannot scroll - must execute a query first."):
            rs.scroll(1)

    def test_fetchone_raises_error(self):
        rs = EmptyResultSet(row_factory=lambda x: x)
        with pytest.raises(ProgrammingError, match="Cannot fetchone - must execute query first."):
            rs.fetchone()

    def test_fetchmany_raises_error(self):
        rs = EmptyResultSet(row_factory=lambda x: x)
        with pytest.raises(ProgrammingError, match="Cannot fetchmany - must execute query first."):
            rs.fetchmany(5)

    def test_fetchall_raises_error(self):
        rs = EmptyResultSet(row_factory=lambda x: x)
        with pytest.raises(ProgrammingError, match="Cannot fetchall - must execute query first."):
            rs.fetchall()


class TestResultSet:
    def test_fetchone(self):
        data = iter([[1, "test"], [2, "data"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        assert rs.fetchone() == [1, "test"]
        assert rs.fetchone() == [2, "data"]
        assert rs.fetchone() is None

    def test_fetchmany(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 2, row_factory=lambda desc: lambda row: row)
        assert rs.fetchmany(2) == [[1, "test"], [2, "data"]]
        assert rs.fetchmany(2) == [[3, "more"]]
        assert rs.fetchmany(2) == []

    def test_fetchmany_no_size(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 2, row_factory=lambda desc: lambda row: row)
        assert rs.fetchmany(None) == [[1, "test"], [2, "data"]]  # Defaults to arraysize=2

    def test_fetchmany_invalid_size(self):
        data = iter([[1, "test"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)

        with pytest.raises(ValueError, match="fetchmany\\(\\) requires a positive size, got 0."):
            rs.fetchmany(0)

        with pytest.raises(ValueError, match="fetchmany\\(\\) requires a positive size, got -5."):
            rs.fetchmany(-5)

    def test_scroll_relative(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        rs.scroll(1)
        assert rs.rownumber == 1
        assert rs.fetchone() == [2, "data"]

    def test_scroll_relative_invalid(self):
        data = iter([[1, "test"], [2, "data"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)

        with pytest.raises(ProgrammingError, match="Cursor can only move forward, got -1."):
            rs.scroll(-1)

    def test_scroll_absolute(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        rs.scroll(1)  # scroll relative to beginning
        assert rs.rownumber == 1
        rs.scroll(2, mode="absolute")  # scroll to absolute last position
        assert rs.rownumber == 2
        assert rs.fetchone() == [3, "more"]

    def test_scroll_absolute_backwards(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        rs.scroll(2, mode="absolute")

        with pytest.raises(ProgrammingError, match="Cannot move cursor backward: currently at row 2, requested 1."):
            rs.scroll(1, mode="absolute")

    def test_scroll_absolute_negative(self):
        data = iter([[1, "test"], [2, "data"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)

        with pytest.raises(ProgrammingError, match="Cursor index cannot be negative, got -1."):
            rs.scroll(-1, mode="absolute")

    def test_scroll_absolute_same_position(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)
        rs.scroll(1, mode="absolute")

        with pytest.raises(ProgrammingError, match="Tried to move cursor to 1, but cursor is already at 1."):
            rs.scroll(1, mode="absolute")

    def test_scroll_exceeding_rows(self):
        data = iter([[1, "test"], [2, "data"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)

        with pytest.raises(IndexError, match="Cursor is exhausted"):
            rs.scroll(10, mode="relative")

    def test_scroll_invalid_mode(self):
        data = iter([[1, "test"]])
        rs = ResultSet(data, ["id"], ["INT"], None, 1, row_factory=lambda desc: lambda row: row)
        with pytest.raises(NotSupportedError, match="Mode must be 'relative' or 'absolute', got invalid"):
            rs.scroll(1, mode="invalid")

    def test_fetchall(self):
        data = iter([[1, "test"], [2, "data"], [3, "more"]])
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=lambda desc: lambda row: row)

        rows = rs.fetchall()
        assert rows == [[1, "test"], [2, "data"], [3, "more"]]
        assert rs.rownumber == 3

        assert rs.fetchall() == []
        assert rs.rownumber == 3

    def test_make_empty(self):
        data = iter([[1, "test"]])
        rf = lambda desc: lambda row: row
        rs = ResultSet(data, ["id", "name"], ["INT", "STRING"], None, 1, row_factory=rf)

        empty_rs = rs.make_empty()
        assert isinstance(empty_rs, EmptyResultSet)
        assert empty_rs.arraysize == 1
        assert empty_rs._row_factory == rf
