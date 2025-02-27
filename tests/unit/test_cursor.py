import decimal
from unittest.mock import AsyncMock
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import httpx
import orjson
import pytest

from pinot_connect._query import Query
from pinot_connect._result_set import Column
from pinot_connect._result_set import EmptyResultSet
from pinot_connect._result_set import ResultSet
from pinot_connect.cursor import AsyncCursor
from pinot_connect.cursor import BaseCursor
from pinot_connect.cursor import Cursor
from pinot_connect.cursor import QueryStatistics
from pinot_connect.cursor import _make_query_statistics
from pinot_connect.exceptions import DatabaseError
from pinot_connect.exceptions import NotSupportedError
from pinot_connect.exceptions import OperationalError
from pinot_connect.exceptions import ProgrammingError
from pinot_connect.options import QueryOptions


@pytest.fixture
def mock_connection():
    connection = MagicMock()
    connection._cursors = set()
    connection.query_options = QueryOptions()
    connection._client.build_request.return_value = MagicMock(spec=httpx.Request)
    connection._client.send = MagicMock()
    return connection


@pytest.fixture
def mock_async_connection():
    connection = MagicMock()
    connection._cursors = set()
    connection.query_options = QueryOptions()
    connection._client.build_request.return_value = MagicMock(spec=httpx.Request)
    connection._client.send = AsyncMock()
    return connection


@pytest.fixture
def base_cursor(mock_connection):
    return BaseCursor(connection=mock_connection, row_factory=lambda x: x)


@pytest.fixture
def cursor(mock_connection):
    return Cursor(connection=mock_connection, row_factory=lambda x: x)


@pytest.fixture
def async_cursor(mock_async_connection):
    return AsyncCursor(connection=mock_async_connection, row_factory=lambda x: x)


def test_make_query_statistics():
    r = {
        "resultTable": {"dataSchema": {"columnNames": ["AirTime"], "columnDataTypes": ["INT"]}, "rows": [[359]]},
        "numRowsResultSet": 1,
        "partialResult": False,
        "exceptions": [],
        "numGroupsLimitReached": False,
        "maxRowsInJoinReached": False,
        "maxRowsInWindowReached": False,
        "timeUsedMs": 20,
        "stageStats": {},
        "maxRowsInOperator": 1,
        "requestId": "93259971000000011",
        "brokerId": "Broker_172.17.0.2_8000",
        "numDocsScanned": 1,
        "totalDocs": 9746,
        "numEntriesScannedInFilter": 0,
        "numEntriesScannedPostFilter": 1,
        "numServersQueried": 0,
        "numServersResponded": 0,
        "numSegmentsQueried": 31,
        "numSegmentsProcessed": 1,
        "numSegmentsMatched": 1,
        "numConsumingSegmentsQueried": 0,
        "numConsumingSegmentsProcessed": 0,
        "numConsumingSegmentsMatched": 0,
        "minConsumingFreshnessTimeMs": 0,
        "numSegmentsPrunedByBroker": 0,
        "numSegmentsPrunedByServer": 30,
        "numSegmentsPrunedInvalid": 0,
        "numSegmentsPrunedByLimit": 30,
        "numSegmentsPrunedByValue": 0,
        "brokerReduceTimeMs": 3,
        "offlineThreadCpuTimeNs": 0,
        "realtimeThreadCpuTimeNs": 0,
        "offlineSystemActivitiesCpuTimeNs": 0,
        "realtimeSystemActivitiesCpuTimeNs": 0,
        "offlineResponseSerializationCpuTimeNs": 0,
        "realtimeResponseSerializationCpuTimeNs": 0,
        "offlineTotalCpuTimeNs": 0,
        "realtimeTotalCpuTimeNs": 0,
        "explainPlanNumEmptyFilterSegments": 0,
        "explainPlanNumMatchAllFilterSegments": 0,
        "traceInfo": {},
        "tablesQueried": ["airlineStats"],
    }
    qs = _make_query_statistics(r)
    assert "resultTable" not in qs
    assert "execptions" not in qs
    del r["resultTable"]
    del r["exceptions"]
    for k, v in qs.items():
        assert r[k] == v


class TestBaseCursor:
    def test_initialization(self, base_cursor, mock_connection):
        assert base_cursor._connection == mock_connection
        assert isinstance(base_cursor._result_set, EmptyResultSet)
        assert base_cursor._closed is False
        assert base_cursor._last_query is None

    def test_description(self, base_cursor):
        mock_description = [Column(name="col1", type_code=int)]

        with patch.object(type(base_cursor._result_set), "description", new_callable=PropertyMock) as mock_property:
            mock_property.return_value = mock_description
            assert base_cursor.description == mock_description

    def test_properties(self, base_cursor):
        assert base_cursor.rowcount == base_cursor._result_set.rowcount
        assert base_cursor.rownumber == base_cursor._result_set.rownumber
        assert base_cursor.arraysize == base_cursor._result_set.arraysize

        assert base_cursor.query_statistics is None
        base_cursor._last_query_statistics = {"foo": "bar"}
        assert base_cursor.query_statistics == {"foo": "bar"}

        assert base_cursor.query is None
        base_cursor._last_query = Query("SELECT * FROM table")
        assert base_cursor.query == "SELECT * FROM table"

    def test_arraysize_setter(self, base_cursor):
        base_cursor.arraysize = 10
        assert base_cursor._result_set.arraysize == 10

    def test_reset(self, base_cursor):
        base_cursor._result_set = ResultSet(iter([]), [], [], None, 1, row_factory=lambda x: x)
        base_cursor._reset()
        assert isinstance(base_cursor._result_set, EmptyResultSet)

    def test_build_request(self, base_cursor, mock_connection):
        request = base_cursor._build_request("SELECT * FROM table")
        mock_connection._client.build_request.assert_called_once()
        assert isinstance(request, httpx.Request)

    def test_handle_response(self, base_cursor):
        response = MagicMock(spec=httpx.Response)
        response.content = orjson.dumps(
            {"resultTable": {"rows": [], "dataSchema": {"columnDataTypes": [], "columnNames": []}}}
        )
        assert base_cursor._handle_response(response) == response

    def test_handle_response_with_exceptions(self, base_cursor):
        response = MagicMock(spec=httpx.Response)
        response.content = orjson.dumps({"exceptions": [{"errorCode": 150, "message": "Some error"}]})

        with patch.object(BaseCursor, "_handle_query_exception") as mock_handle_exception:
            base_cursor._handle_response(response)
            mock_handle_exception.assert_called_once()

    def test_handle_response_with_http_error(self, base_cursor):
        response = MagicMock(spec=httpx.Response)
        response.status_code = 500
        response.content = orjson.dumps({})

        with patch.object(BaseCursor, "_handle_query_http_error_code") as mock_handle_http_error:
            base_cursor._handle_response(response)
            mock_handle_http_error.assert_called_once()

    def test_handle_query_exception(self, base_cursor):
        json_response = {"exceptions": [{"errorCode": 150, "message": "Some error"}]}
        with pytest.raises(DatabaseError, match=r"\[Pinot Error 150\] Some error"):
            base_cursor._handle_query_exception(json_response)

    def test_handle_query_http_error_code(self, base_cursor):
        response = MagicMock(spec=httpx.Response)
        response.status_code = 500
        response.text = "Server error"
        with pytest.raises(OperationalError, match="Server error"):
            base_cursor._handle_query_http_error_code(response)

        response.status_code = 400
        response.text = "Query error"
        with pytest.raises(ProgrammingError, match="Query error"):
            base_cursor._handle_query_http_error_code(response)

    def test_check_servers_responded(self, base_cursor):
        r = {"numServersQueried": 1, "numServersResponded": 0}
        with pytest.raises(DatabaseError, match="Queried 1 server\(s\), but 0 responded"):
            base_cursor._check_servers_responded(r)

    def test_close(self, base_cursor, mock_connection):
        base_cursor._close()
        assert base_cursor._closed is True
        assert base_cursor not in mock_connection._cursors

    def test_next(self, base_cursor):
        base_cursor._result_set.fetchone = MagicMock(side_effect=[["row1"], ["row2"], None])

        assert base_cursor._next() == ["row1"]
        assert base_cursor._next() == ["row2"]

        with pytest.raises(StopIteration):
            base_cursor._next()

    def test_generate_rows(self, base_cursor):
        types = ["STRING", "INT", "BIG_DECIMAL"]
        rows = [["text", 1, "3.14"], ["more", 2, "2.7"]]

        generated_rows = list(base_cursor._generate_rows(types, rows))

        assert generated_rows == [["text", 1, decimal.Decimal("3.14")], ["more", 2, decimal.Decimal("2.7")]]

    def test_mogrify(self, base_cursor):
        assert (
            base_cursor.mogrify("SELECT * FROM table WHERE foo=%s", ("foo",)) == "SELECT * FROM table WHERE foo='foo'"
        )


class TestCursor:
    def test_execute(self, cursor, mock_connection):
        mock_response = MagicMock(spec=httpx.Response, content=b"{}", status_code=200)
        mock_connection._client.send.return_value = mock_response
        response = cursor.execute("SELECT * FROM table")
        assert response == mock_response

    def test_execute_error(self, cursor, mock_connection):
        mock_connection._client.send.side_effect = Exception("Network error")
        with pytest.raises(DatabaseError, match="Failed to execute query"):
            cursor.execute("SELECT * FROM table")

    def test_executemany(self, cursor):
        with pytest.raises(NotSupportedError, match="The dbapi for apache pinot is read only"):
            cursor.executemany("INSERT INTO table VALUES (?, ?)", [(1, "a")])

    def test_fetchone(self, cursor):
        cursor._result_set.fetchone = MagicMock(return_value=["row1"])
        assert cursor.fetchone() == ["row1"]

    def test_fetchmany(self, cursor):
        cursor._result_set.fetchmany = MagicMock(return_value=[["row1"], ["row2"]])
        assert cursor.fetchmany(2) == [["row1"], ["row2"]]

    def test_fetchall(self, cursor):
        cursor._result_set.fetchall = MagicMock(return_value=[["row1"], ["row2"]])
        assert cursor.fetchall() == [["row1"], ["row2"]]

    def test_scroll(self, cursor):
        cursor._result_set.scroll = MagicMock()
        cursor.scroll(2, mode="absolute")
        cursor._result_set.scroll.assert_called_once_with(2, mode="absolute")

    def test_close(self, cursor):
        cursor.close()
        assert cursor._closed is True

    def test_iterator(self, cursor):
        cursor._result_set.fetchone = MagicMock(side_effect=[["row1"], ["row2"], None])

        results = list(iter(cursor))
        assert results == [["row1"], ["row2"]]

    def test_context_manager(self, cursor):
        with patch.object(cursor, "close") as mock_close:
            with cursor as cur:
                assert cur is cursor
            mock_close.assert_called_once()


@pytest.mark.asyncio
class TestAsyncCursor:
    async def test_scroll(self, async_cursor):
        async_cursor._result_set.scroll = MagicMock()
        await async_cursor.scroll(2, mode="absolute")
        async_cursor._result_set.scroll.assert_called_once_with(2, mode="absolute")

    async def test_execute(self, async_cursor, mock_async_connection):
        mock_response = MagicMock(spec=httpx.Response, content=b"{}", status_code=200)
        mock_async_connection._client.send.return_value = mock_response
        response = await async_cursor.execute("SELECT * FROM table")
        assert response == mock_response

    async def test_execute_error(self, async_cursor, mock_async_connection):
        mock_async_connection._client.send.side_effect = Exception("Network error")
        with pytest.raises(DatabaseError, match="Failed to make query request to server"):
            await async_cursor.execute("SELECT * FROM table")

    async def test_executemany(self, async_cursor):
        with pytest.raises(NotSupportedError, match="The dbapi for apache pinot is read only"):
            await async_cursor.executemany("INSERT INTO table VALUES (?, ?)", [(1, "a")])

    async def test_fetchone(self, async_cursor):
        async_cursor._result_set.fetchone = MagicMock(return_value=["row1"])
        assert await async_cursor.fetchone() == ["row1"]

    async def test_fetchmany(self, async_cursor):
        async_cursor._result_set.fetchmany = MagicMock(return_value=[["row1"], ["row2"]])
        assert await async_cursor.fetchmany(2) == [["row1"], ["row2"]]

    async def test_fetchall(self, async_cursor):
        async_cursor._result_set.fetchall = MagicMock(return_value=[["row1"], ["row2"]])
        assert await async_cursor.fetchall() == [["row1"], ["row2"]]

    async def test_close(self, async_cursor):
        await async_cursor.close()
        assert async_cursor._closed is True

    async def test_iteration(self, async_cursor):
        async_cursor._result_set.fetchone = MagicMock(side_effect=[["row1"], ["row2"], None])

        rows = [row async for row in async_cursor]

        assert rows == [["row1"], ["row2"]]

    async def test_async_context_manager(self, async_cursor):
        with patch.object(async_cursor, "close", new_callable=AsyncMock) as mock_close:
            async with async_cursor as cur:
                assert cur is async_cursor
            mock_close.assert_called_once()
