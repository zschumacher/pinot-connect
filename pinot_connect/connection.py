from __future__ import annotations

import dataclasses
import typing as t

import httpx
from httpx._client import BaseClient
from typing_extensions import Self

from .context import CoroContextManager
from .cursor import AsyncCursor
from .cursor import BaseCursor
from .cursor import Cursor
from .exceptions import *
from .options import ClientOptions
from .options import QueryOptions
from .rows import RowFactory
from .rows import RowType
from .rows import tuple_row

__all__ = [
    "BaseConnection",
    "Connection",
    "AsyncConnection",
]

_CursorType = t.TypeVar("_CursorType", bound=BaseCursor)
_ClientType = t.TypeVar("_ClientType", bound=BaseClient)


class BaseConnection(t.Generic[_CursorType, _ClientType]):
    Error = Error
    InterfaceError = Error
    DatabaseError = DatabaseError
    DataError = DataError
    OperationalError = OperationalError
    InternalError = InternalError
    ProgrammingError = ProgrammingError
    NotSupportedError = NotSupportedError

    def __init__(
        self,
        client: _ClientType,
        *,
        query_options: QueryOptions | None = None,
    ):
        """Base class for building connections to Apache Pinot

        Args:
            client: an instance of subclass of httpx.Client
            query_options: *(optional)*: global query options for all queries made from the connection
        """
        self._client = client
        self._cursors: set[_CursorType] = set()
        self.query_options = query_options or QueryOptions()

    @classmethod
    def _connect(
        cls,
        client: type[_ClientType],
        *,
        host: str,
        port: int = 8099,
        username: str | None,
        password: str | None,
        scheme: t.Literal["http", "https"],
        database: str | None,
        query_options: QueryOptions | None,
        client_options: ClientOptions | None,
    ) -> Self:
        headers = {"database": database} if database else None
        basic_auth = httpx.BasicAuth(username, password) if username and password else None
        safe_client_options = dataclasses.asdict(client_options) if client_options is not None else {}

        c = client(
            base_url=f"{scheme}://{host}:{port}",
            auth=basic_auth,
            headers=headers,
            **safe_client_options,
        )
        return cls(c, query_options=query_options)

    @property
    def closed(self) -> bool:
        """`True` if connection's client is closed"""
        return self._client.is_closed

    def _build_cursor(
        self,
        cursor: type[_CursorType],
        query_options: QueryOptions | None,
        row_factory: RowFactory[RowType] | None,
    ) -> _CursorType:
        if self.closed:
            raise ProgrammingError("Cannot create a cursor: the connection is closed.")
        c = cursor(self, query_options=query_options, row_factory=row_factory or tuple_row)
        self._cursors.add(c)
        return c


class Connection(BaseConnection[Cursor, httpx.Client]):
    @classmethod
    def connect(
        cls,
        host: str,
        port: int = 8099,
        username: str | None = None,
        password: str | None = None,
        scheme: t.Literal["http", "https"] = "http",
        database: str | None = None,
        query_options: QueryOptions | None = None,
        client_options: ClientOptions | None = None,
    ) -> Self:
        """Constructor for building a client and returning a connection

        Args:
            host: the hostname of your apache pinot broker
            port: *(optional)* the port of your apache pinot broker, defaults to `8099`
            username: *(optional)*: the username to use, if auth is enabled
            password: *(optional)*: the password to use, if auth is enabled
            scheme: *(optional)*: the scheme to use, defaults to `http`
            database: *(optional)*: the database/tenant to use
            query_options: *(optional)*: global query options for all queries made from the connection
            client_options: *(optional)*: httpx client options for all queries made from the connection
        """
        return cls._connect(
            httpx.Client,
            host=host,
            port=port,
            username=username,
            password=password,
            scheme=scheme,
            database=database,
            query_options=query_options,
            client_options=client_options,
        )

    def commit(self):  # pragma: no cover
        pass

    @t.overload
    def cursor(
        self,
        *,
        query_options: QueryOptions | None = None,
        row_factory: RowFactory[RowType],
    ) -> Cursor[RowType]:
        ...

    @t.overload
    def cursor(self, *, query_options: QueryOptions | None = None) -> Cursor[tuple]:
        ...

    def cursor(self, *, query_options: QueryOptions | None = None, row_factory=tuple_row):
        """Builds a new pinot_connect.Cursor object using the connection.

        Args:
            query_options: *(optional)*: query options to be used by cursor, overrides any options set at connection level
            row_factory: *(optional)*: RowFactory type to use to build rows fetched from cursor, defaults to returning
                tuples
        """
        return self._build_cursor(Cursor, query_options, row_factory)

    def close(self):
        """Close the connection and cleans up resources.

        Closes all open cursors and all open TCP connections in the client.
        """
        for cursor in list(self._cursors):  # copy to ensure we don't modify set during iteration
            cursor.close()

        self._cursors.clear()

        if not self.closed:  # pragma: no branch
            self._client.close()

    def __enter__(self) -> Self:
        self._client.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._client.__exit__(exc_type, exc_val, exc_tb)
        self.close()


class AsyncConnection(BaseConnection[AsyncCursor, httpx.AsyncClient]):
    @classmethod
    def connect(
        cls,
        host: str,
        port: int = 8099,
        username: str | None = None,
        password: str | None = None,
        scheme: t.Literal["http", "https"] = "http",
        database: str | None = None,
        query_options: QueryOptions | None = None,
        client_options: ClientOptions | None = None,
    ) -> CoroContextManager[Self]:
        """Constructor for building a client and returning an async connection wrapped in
        a CoroContextManager object.  This allows this method to both be awaited and be used
        with async with (without having to do async with await).

        Args:
            host: the hostname of your apache pinot broker
            port: the port of your apache pinot broker, defaults to `8099`
            username: *(optional)*: the username to use, if auth is enabled
            password: *(optional)*: the password to use, if auth is enabled
            scheme: *(optional)*: the scheme to use, defaults to `http`
            database: *(optional)*: the database/tenant to use
            query_options: *(optional)*: global query options for all queries made from the connection
            client_options: *(optional)*: httpx client options for all queries made from the connection

        Returns: an instance of `pinot_connect.AsyncConnection` wrapped in a CoroContextManager
        """
        super_connect = super()._connect

        async def connect_():
            return super_connect(
                httpx.AsyncClient,
                host=host,
                port=port,
                username=username,
                password=password,
                scheme=scheme,
                database=database,
                query_options=query_options,
                client_options=client_options,
            )

        return CoroContextManager(connect_())

    async def commit(self):  # pragma: no cover
        """Not implemented - read only interface"""  # pragma: no cover
        pass

    @t.overload
    def cursor(
        self,
        *,
        query_options: QueryOptions | None = None,
        row_factory: RowFactory[RowType],
    ) -> CoroContextManager[AsyncCursor[RowType]]:
        ...

    @t.overload
    def cursor(self, *, query_options: QueryOptions | None = None) -> CoroContextManager[AsyncCursor[tuple]]:
        ...

    def cursor(self, query_options: QueryOptions | None = None, row_factory=tuple_row):
        """Builds a new pinot_connect.AsyncCursor object using the connection.

        Args:
            query_options: *(optional)*: query options to be used by cursor, overrides any options set at connection level
            row_factory: *(optional)*: RowFactory type to use to build rows fetched from cursor, defaults to returning
                tuples
        """

        async def cursor_():
            return self._build_cursor(AsyncCursor, query_options, row_factory)

        return CoroContextManager(cursor_())

    async def close(self):
        """Close the connection and cleans up resources.

        Closes all open cursors and all open TCP connections in the client.
        """
        for cursor in list(self._cursors):  # copy to ensure we don't modify set during iteration
            await cursor.close()

        self._cursors.clear()

        if not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        await self._client.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._client.__aexit__(exc_type, exc_val, exc_tb)
        await self.close()
