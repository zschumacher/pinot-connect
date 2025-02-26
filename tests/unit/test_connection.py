from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

from pinot_connect.connection import AsyncConnection
from pinot_connect.connection import BaseConnection
from pinot_connect.connection import Connection
from pinot_connect.cursor import AsyncCursor
from pinot_connect.cursor import Cursor
from pinot_connect.exceptions import ProgrammingError


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.is_closed = False
    return client


@pytest.fixture
def mock_async_client():
    client = AsyncMock()
    client.is_closed = False
    return client


class TestBaseConnection:
    def test_connection_initialization(self, mock_client):
        connection = BaseConnection(mock_client)
        assert connection._client is mock_client
        assert connection.closed is False

    def test_build_cursor(self, mock_client):
        connection = BaseConnection(mock_client)
        cursor_class = MagicMock()
        query_options = Mock()
        row_factory = Mock()
        connection._build_cursor(cursor_class, query_options, row_factory)
        cursor_class.assert_called_once_with(connection, query_options=query_options, row_factory=row_factory)

    def test_build_cursor_fails_when_connection_closed(self, mock_client):
        connection = BaseConnection(mock_client)
        mock_client.is_closed = True
        with pytest.raises(ProgrammingError, match="Cannot create a cursor: the connection is closed."):
            connection._build_cursor(MagicMock(), None, None)


class TestConnection:
    def test_connection_creation(self):
        connection = Connection.connect(host="localhost")
        assert isinstance(connection, Connection)
        assert connection.closed is False

    def test_cursor_creation(self, mock_client):
        connection = Connection(mock_client)
        cursor_mock = MagicMock()
        connection._build_cursor = cursor_mock
        query_options = MagicMock()
        row_factory = MagicMock()
        connection.cursor(query_options=query_options, row_factory=row_factory)
        cursor_mock.assert_called_with(Cursor, query_options, row_factory)

    def test_close_connection(self):
        connection = Connection.connect(host="localhost")
        mock_cursor = Mock()
        connection._client._state = "OPEN"
        connection._cursors.add(mock_cursor)
        connection.close()
        mock_cursor.close.assert_called_once()
        assert connection.closed is True

    def test_context_manager(self):
        with Connection.connect(host="localhost") as connection:
            assert not connection.closed
        assert connection.closed


class TestAsyncConnection:
    @pytest.mark.asyncio
    async def test_connection_creation(self, mock_async_client):
        async with await AsyncConnection.connect(host="localhost") as connection:
            assert isinstance(connection, AsyncConnection)
            assert connection.closed is False

    @pytest.mark.asyncio
    async def test_cursor_creation(self, mock_async_client):
        async with await AsyncConnection.connect(host="localhost") as connection:
            connection._build_cursor = MagicMock()
            query_options = MagicMock()
            row_factory = MagicMock()
            await connection.cursor(query_options=query_options, row_factory=row_factory)
            connection._build_cursor.assert_called_once_with(AsyncCursor, query_options, row_factory)

    @pytest.mark.asyncio
    async def test_close_connection(self, mock_async_client):
        connection = await AsyncConnection.connect(host="localhost")
        connection._client._state = "OPEN"
        mock_cursor = AsyncMock()
        connection._cursors.add(mock_cursor)
        await connection.close()
        mock_cursor.close.assert_awaited_once()
        assert connection._client.is_closed

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_async_client):
        async with AsyncConnection.connect(host="localhost") as connection:
            assert not connection.closed
        assert connection.closed
