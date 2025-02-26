import pytest

from pinot_connect._decorators import acheck_cursor_open
from pinot_connect._decorators import check_cursor_open
from pinot_connect.exceptions import ProgrammingError


class MockCursor:
    def __init__(self, closed: bool):
        self.closed = closed


@check_cursor_open
def mock_function(cursor: MockCursor):
    return "Success"


@acheck_cursor_open
async def async_mock_function(cursor: MockCursor):
    return "Success"


class TestCheckCursorOpen:
    def test_open_cursor(self):
        cursor = MockCursor(closed=False)
        assert mock_function(cursor) == "Success"

    def test_closed_cursor(self):
        cursor = MockCursor(closed=True)
        with pytest.raises(ProgrammingError, match="Operation failed: Cannot call mock_function on closed cursor."):
            mock_function(cursor)


class TestACheckCursorOpen:
    @pytest.mark.asyncio
    async def test_open_cursor(self):
        cursor = MockCursor(closed=False)
        result = await async_mock_function(cursor)
        assert result == "Success"

    @pytest.mark.asyncio
    async def test_closed_cursor(self):
        cursor = MockCursor(closed=True)
        with pytest.raises(
            ProgrammingError, match="Operation failed: Cannot call async_mock_function on closed cursor."
        ):
            await async_mock_function(cursor)
