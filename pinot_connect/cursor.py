from __future__ import annotations

import asyncio
import typing as t

import httpx
import orjson
from httpx import USE_CLIENT_DEFAULT
from typing_extensions import Self

from ._decorators import acheck_cursor_open
from ._decorators import check_cursor_open
from ._query import Query
from ._result_set import Column
from ._result_set import EmptyResultSet
from ._result_set import ResultSet
from ._result_set import _BaseResultSet
from ._type_converters import build_converters
from .exceptions import *
from .options import QueryOptions
from .options import RequestOptions
from .rows import RowFactory
from .rows import RowType

__all__ = ["BaseCursor", "Cursor", "AsyncCursor"]

if t.TYPE_CHECKING:
    from .connection import AsyncConnection
    from .connection import BaseConnection
    from .connection import Connection

_ConnectionType = t.TypeVar("_ConnectionType", bound="BaseConnection")


class BaseCursor(t.Generic[_ConnectionType, RowType]):
    __slots__ = (
        "_connection",
        "_query_options",
        "_result_set",
        "_closed",
        "_rowcount",
        "_arraysize",
        "_last_query",
        "_row_factory",
        "_convert_binary",
    )

    _result_set: _BaseResultSet[RowType]

    def __init__(
        self,
        connection: _ConnectionType,
        row_factory: RowFactory[RowType],
        *,
        query_options: QueryOptions | None = None,
    ):
        self._query_options = QueryOptions.merge(connection.query_options, query_options or QueryOptions())
        self._connection = connection
        self._result_set: _BaseResultSet[RowType] = EmptyResultSet[RowType](row_factory)
        self._closed = False
        self._last_query: Query | None = None

        # noinspection PyProtectedMember
        if self not in connection._cursors:  # pragma: no branch
            # noinspection PyProtectedMember
            connection._cursors.add(self)

    @property
    def description(self) -> list[Column] | None:
        """Description of query result

        Only name and type code (index 0 and 1) will ever be populated for this
        implementation
        """
        return self._result_set.description

    @property
    def connection(self) -> _ConnectionType:
        """Pointer to the connection used to create this cursor"""
        return self._connection

    @property
    def rownumber(self) -> int | None:
        """Current position of cursor"""
        return self._result_set.rownumber

    @property
    def rowcount(self) -> int | None:
        """Number of rows returned by last executed query"""
        return self._result_set.rowcount

    @property
    def closed(self) -> bool:
        """`True` if the cursor is closed"""
        return self._closed

    @property
    def arraysize(self) -> int:
        """Number of rows to fetch with fetchmany if no size is specified in the method call"""
        return self._result_set.arraysize

    @arraysize.setter
    def arraysize(self, value: int):
        self._result_set.arraysize = value

    @property
    def query(self) -> str | None:
        """Last executed query"""
        return self._last_query.operation if self._last_query else None

    def _build_request(
        self,
        operation: str,
        params: dict | tuple | list | None = None,
        *,
        query_options: QueryOptions | None = None,
        request_options: RequestOptions | None = None,
    ) -> httpx.Request:
        query_options = QueryOptions.merge(self._query_options, query_options or QueryOptions())
        query = Query(operation, params)
        self._last_query = query
        http_params = {"queryOptions": QueryOptions.to_kv_pair(query_options.asdict())} if query_options else None
        # noinspection PyProtectedMember
        return self._connection._client.build_request(
            "POST",
            "/query",
            params=http_params,
            json={"sql": query.operation_with_params},
            timeout=request_options.timeout if request_options and request_options.timeout else USE_CLIENT_DEFAULT,
            cookies=request_options.cookies if request_options else None,
            extensions=request_options.extensions if request_options else None,
        )

    def _reset(self):
        # if the result set is already an EmptyResultSet, this can be a noop
        if isinstance(self._result_set, ResultSet):
            self._result_set = self._result_set.make_empty()

    def _handle_response(self, r: httpx.Response) -> httpx.Response:
        json_response = orjson.loads(r.content)
        if "resultTable" in json_response:
            self._handle_query_result(json_response)
        elif "exceptions" in json_response and json_response["exceptions"]:  # pragma: no branch
            self._handle_query_exception(json_response)  # raises exception based on pinot error code
        elif httpx.codes.is_error(r.status_code):  # pragma: no branch
            self._handle_query_http_error_code(r)  # raises ProgrammingError

        return r

    def _generate_rows(self, types: list[str], rows: list[list]) -> t.Iterator[list]:
        converters = build_converters(types)
        for row in rows:
            for index, converter in converters.items():
                row[index] = converter(row[index])
            yield row

    def _handle_query_result(self, json_response: dict) -> None:
        rows = json_response["resultTable"]["rows"]
        types = json_response["resultTable"]["dataSchema"]["columnDataTypes"]
        self._result_set = ResultSet[RowType](
            self._generate_rows(types, rows),
            columns=json_response["resultTable"]["dataSchema"]["columnNames"],
            types=types,
            rowcount=len(json_response["resultTable"]["rows"]),
            arraysize=self._result_set.arraysize,  # copy arraysize from last result set
            row_factory=self._result_set._row_factory,
        )

    def _handle_query_exception(self, json_response: dict):
        # Yet to see more than one object in exception array, so making an assumption here...
        exception = json_response["exceptions"][0]
        error_code, message = exception["errorCode"], exception["message"]
        DbapiException = CODE_EXCEPTION_MAP.get(error_code, Error)
        raise DbapiException(f"[Pinot Error {error_code}] {message}")

    def _handle_query_http_error_code(self, response: httpx.Response):
        if response.status_code >= 500:
            raise OperationalError(f"Server error [{response.status_code}]: {response.text}")
        elif response.status_code == 400:
            raise ProgrammingError(f"Query error [{response.status_code}]: {response.text}")
        raise ProgrammingError(f"Unexpected HTTP error [{response.status_code}]: {response.text}")  # pragma: no cover

    def _close(self):
        self._reset()
        self._closed = True
        # noinspection PyProtectedMember
        self.connection._cursors.discard(self)

    def _next(self):
        row = self._result_set.fetchone()
        if row is None:
            raise StopIteration
        return row

    def mogrify(self, operation: str, params: dict | tuple | list | None = None) -> str:
        """Take an operation and params and return the operation after param binding"""
        return Query(operation, params).operation_with_params


class Cursor(BaseCursor["Connection", RowType]):
    @check_cursor_open
    def scroll(self, value: int, *, mode: t.Literal["relative", "absolute"] = "relative") -> None:
        """Move the cursor in the result set to a new position using the mode.

        If mode=`relative` (default), treat the passed value as an offset relative to the current position in the result
        set. If mode=`absolute`, move to the passed position.

        Args:
            value: The offset if in `relative` mode; the target position if in `absolute` mode
            mode: *(optional)* determines the model to use for the scroll.  Default: `relative`
        """
        return self._result_set.scroll(value, mode=mode)

    @check_cursor_open
    def execute(
        self,
        operation: str,
        params: dict | tuple | list | None = None,
        *,
        query_options: QueryOptions | None = None,
        request_options: RequestOptions | None = None,
    ) -> httpx.Response:
        """Execute a query against the *Pinot* broker

        The query returns the `httpx.Response` from the request, which you normally will not need; however,
        it may be useful for debugging.

        Args:
            operation: the sql operation to send to the broker
            params: *(optional)* sql params to bind to the operation
            query_options: *(optional)* query options that override what is set on cursor/connection
            request_options: *(optional)* request options to use for this specific query.  Can override timeout and
                cookies from cursor/connection
        """
        request = self._build_request(operation, params=params, query_options=query_options)
        try:
            # noinspection PyProtectedMember
            response = self.connection._client.send(request)
        except Exception as e:
            raise DatabaseError("Failed to execute query") from e
        return self._handle_response(response)

    def executemany(self, operation: str, parameters: t.Sequence[tuple] | t.Sequence[dict]):
        raise NotSupportedError(
            "The dbapi for apache pinot is read only, thus executemany is not implemented on Cursor"
        )

    @check_cursor_open
    def fetchone(self) -> RowType | None:
        """Fetch the next record from the current result set or `None` if exhausted

        uses passed `row_factory` to cursor to determine `RowType` of returned row
        """
        return self._result_set.fetchone()

    @check_cursor_open
    def fetchmany(self, size: int | None = None) -> list[RowType]:
        """Fetch the next size records from the current result set.  If size is not passed, the value
        of the `arraysize` property will be used instead.

        Uses passed `row_factory` to cursor to determine `RowType` of returned rows.

        > This method can return fewer records than requested.  For example, if a size of 3 is passed, but the result
        > set only has two records remaining, the two records will be returned only.

        Args:
            size: *(optional)* number of records to fetch - if not passed, will use arraysize property instead
        """
        return self._result_set.fetchmany(size)

    @check_cursor_open
    def fetchall(self) -> list[RowType]:
        """Fetch all remaining records from the current result set.  Returns empty list if no
        records remaining or result set is empty.

        Uses passed `row_factory` to cursor to determine `RowType` of returned rows.
        """
        rows = self._result_set.fetchall()
        return rows

    def setinputsizes(self, sizes: t.Sequence[int | type | None]) -> None:  # pragma: no cover
        pass

    def setoutputsize(self, size: int, column: int | None = None) -> None:  # pragma: no cover
        pass

    def close(self) -> None:
        """Close cursor and cleanup resources"""
        self._close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __iter__(self) -> Self:
        return self

    def __next__(self) -> RowType:
        return self._next()


class AsyncCursor(BaseCursor["AsyncConnection", RowType]):
    @acheck_cursor_open
    async def scroll(self, value: int, *, mode: t.Literal["relative", "absolute"] = "relative") -> None:
        """Move the cursor in the result set to a new position using the mode.

        If mode=`relative` (default), treat the passed value as an offset relative to the current position in the result
        set. If mode=`absolute`, move to the passed position.

        Args:
            value: The offset if in `relative` mode; the target position if in `absolute` mode
            mode: *(optional)* determines the model to use for the scroll.  Default: `relative`
        """
        return self._result_set.scroll(value, mode=mode)

    @acheck_cursor_open
    async def execute(
        self,
        operation: str,
        params: dict | tuple | list | None = None,
        *,
        query_options: QueryOptions | None = None,
    ) -> httpx.Response:
        """Execute a query against the *Pinot* broker

        The query returns the `httpx.Response` from the request, which you normally will not need; however,
        it may be useful for debugging.

        Args:
            operation: the sql operation to send to the broker
            params: *(optional)* sql params to bind to the operation
            query_options: *(optional)* query options that override what is set on cursor/connection
        """
        request = self._build_request(operation, params=params, query_options=query_options)
        try:
            # noinspection PyProtectedMember
            response = await self.connection._client.send(request)
        except Exception as e:
            raise DatabaseError("Failed to make query request to server") from e
        return self._handle_response(response)

    async def executemany(self, operation: str, parameters: t.Sequence[tuple] | t.Sequence[dict]):
        raise NotSupportedError(
            "The dbapi for apache pinot is read only, thus executemany is not implemented on AsyncCursor"
        )

    @acheck_cursor_open
    async def fetchone(self) -> RowType | None:
        """Fetch the next record from the current result set or `None` if exhausted

        Uses passed `row_factory` to cursor to determine `RowType` of returned row
        """
        return self._result_set.fetchone()

    @acheck_cursor_open
    async def fetchmany(self, size: int | None = None) -> list[RowType]:
        """Fetch the next size records from the current result set.  If size is not passed, the value
        of the `arraysize` property will be used instead.

        Uses passed `row_factory` to cursor to determine `RowType` of returned rows.

        > This method can return fewer records than requested.  For example, if a size of 3 is passed, but the result
        > set only has two records remaining, the two records will be returned only.

        Args:
            size: *(optional)* number of records to fetch - if not passed, will use arraysize property instead
        """
        return self._result_set.fetchmany(size)

    @acheck_cursor_open
    async def fetchall(self) -> list[RowType]:
        """Fetch all remaining records from the current result set.  Returns empty list if no
        records remaining or result set is empty.

        Uses passed `row_factory` to cursor to determine `RowType` of returned rows.
        """
        return self._result_set.fetchall()

    async def setinputsizes(self, sizes: t.Sequence[int | type | None]) -> None:  # pragma: no cover
        pass

    async def setoutputsize(self, size: int, column: int | None = None) -> None:  # pragma: no cover
        pass

    async def close(self) -> None:
        """Close cursor and cleanup resources"""
        self._close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __aiter__(self) -> Self:
        return self

    @acheck_cursor_open
    async def __anext__(self) -> RowType:
        await asyncio.sleep(0)  # yield control to loop while iterating to prevent long blocks
        try:
            return self._next()
        except StopIteration:
            raise StopAsyncIteration
