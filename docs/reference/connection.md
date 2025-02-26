<a id="pinot_connect.connection"></a>

# pinot\_connect.connection

<a id="pinot_connect.connection.BaseConnection"></a>

---
## BaseConnection

```python
class BaseConnection(t.Generic[_CursorType, _ClientType])
```

<a id="pinot_connect.connection.BaseConnection.__init__"></a>

#### \_\_init\_\_

```python
def __init__(client: _ClientType,
             *,
             query_options: QueryOptions | None = None)
```

Base class for building connections to Apache Pinot

**Arguments**:

- `client` - an instance of subclass of httpx.Client
- `query_options` - *(optional)*: global query options for all queries made from the connection

<a id="pinot_connect.connection.BaseConnection.closed"></a>

#### closed

```python
@property
def closed() -> bool
```

`True` if connection's client is closed

<a id="pinot_connect.connection.Connection"></a>

---
## Connection

```python
class Connection(BaseConnection[Cursor, httpx.Client])
```

<a id="pinot_connect.connection.Connection.connect"></a>

#### connect

```python
@classmethod
def connect(cls,
            host: str,
            port: int = 8099,
            username: str | None = None,
            password: str | None = None,
            scheme: t.Literal["http", "https"] = "http",
            database: str | None = None,
            query_options: QueryOptions | None = None,
            client_options: ClientOptions | None = None) -> Self
```

Constructor for building a client and returning a connection

**Arguments**:

- `host` - the hostname of your apache pinot broker
- `port` - *(optional)* the port of your apache pinot broker, defaults to `8099`
- `username` - *(optional)*: the username to use, if auth is enabled
- `password` - *(optional)*: the password to use, if auth is enabled
- `scheme` - *(optional)*: the scheme to use, defaults to `http`
- `database` - *(optional)*: the database/tenant to use
- `query_options` - *(optional)*: global query options for all queries made from the connection
- `client_options` - *(optional)*: httpx client options for all queries made from the connection

<a id="pinot_connect.connection.Connection.cursor"></a>

#### cursor

```python
def cursor(*,
           query_options: QueryOptions | None = None,
           row_factory=tuple_row)
```

Builds a new pinot_connect.Cursor object using the connection.

**Arguments**:

- `query_options` - *(optional)*: query options to be used by cursor, overrides any options set at connection level
- `row_factory` - *(optional)*: RowFactory type to use to build rows fetched from cursor, defaults to returning
  tuples

<a id="pinot_connect.connection.Connection.close"></a>

#### close

```python
def close()
```

Close the connection and cleans up resources.

Closes all open cursors and all open TCP connections in the client.

<a id="pinot_connect.connection.AsyncConnection"></a>

---
## AsyncConnection

```python
class AsyncConnection(BaseConnection[AsyncCursor, httpx.AsyncClient])
```

<a id="pinot_connect.connection.AsyncConnection.connect"></a>

#### connect

```python
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
        client_options: ClientOptions | None = None
) -> CoroContextManager[Self]
```

Constructor for building a client and returning an async connection wrapped in
a CoroContextManager object.  This allows this method to both be awaited and be used
with async with (without having to do async with await).

**Arguments**:

- `host` - the hostname of your apache pinot broker
- `port` - the port of your apache pinot broker, defaults to `8099`
- `username` - *(optional)*: the username to use, if auth is enabled
- `password` - *(optional)*: the password to use, if auth is enabled
- `scheme` - *(optional)*: the scheme to use, defaults to `http`
- `database` - *(optional)*: the database/tenant to use
- `query_options` - *(optional)*: global query options for all queries made from the connection
- `client_options` - *(optional)*: httpx client options for all queries made from the connection
  
- `Returns` - an instance of `pinot_connect.AsyncConnection` wrapped in a CoroContextManager

<a id="pinot_connect.connection.AsyncConnection.commit"></a>

#### commit

```python
async def commit()
```

Not implemented - read only interface

<a id="pinot_connect.connection.AsyncConnection.cursor"></a>

#### cursor

```python
def cursor(query_options: QueryOptions | None = None, row_factory=tuple_row)
```

Builds a new pinot_connect.AsyncCursor object using the connection.

**Arguments**:

- `query_options` - *(optional)*: query options to be used by cursor, overrides any options set at connection level
- `row_factory` - *(optional)*: RowFactory type to use to build rows fetched from cursor, defaults to returning
  tuples

<a id="pinot_connect.connection.AsyncConnection.close"></a>

#### close

```python
async def close()
```

Close the connection and cleans up resources.

Closes all open cursors and all open TCP connections in the client.

