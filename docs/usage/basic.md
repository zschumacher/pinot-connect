This page describes the basic objects and methods in `pinot_connect` and how to use them.

Cursors and connections are highly configurable.  While this page just describes basic usage, the 
[**options tutorial**](options.md) and the [**options reference**](../reference/options.md) go into more detail.

---
## [Connections](../reference/connection.md)
The connection is the main entry point to using pinot_connect.  While connections *can* be constructed directly, you will 
typically use `pinot_connect.connect` or `pinot_connect.AsyncConnection.connect` as it handles creating and configuring the `httpx` 
client for you.

!!! example
    === "sync"
        ``` py title="Using the connection factory"
        import pinot_connect
        
        # use it as a context manager
        with pinot_connect.connect(host="localhost") as conn:
            # pinot_connect.Connection
    
        # don't use it as a context manager, close it later
        conn = pinot_connect.connect(host="localhost")
        # do stuff
        conn.close()
        ```
    === "async"
        ```py title="Using the async connection factory"
        import pinot_connect

        async def main():
            # use it as a context manaager
            async with pinot_connect.AsyncConnection.connect(host="localhost) as conn:
                # pinot_connect.AsyncConnection

            # don't use it as a context manager, close it later
            conn = await pinot_connect.AsyncConnection.connect(host="localhost")
            # do stuff
            await conn.close()
        ```

- Connections are designed to be reused.
- Unlike traditional database drivers, pinot_connect does not require a connection pool—httpx handles this internally. In most 
  cases, a single connection per application is sufficient.
- The second request (and subsequent ones) will always be **faster** than the first, as `httpx` keeps the connection alive.
- Standard connections are **thread-safe**, while async connections are **task-safe**.

Connection factories take the following arguments:

- `host` - the hostname of your apache pinot broker
- `port` - *(optional*) the port of your apache pinot broker, defaults to `8099`
- `username` - *(optional)*: the username to use, if basic auth is enabled on the cluster
- `password` - *(optional)*: the password to use, if basic auth is enabled on the cluster
- `scheme` - *(optional)*: the scheme to use, defaults to `http`.  Must be one of `http` or `https`.  Additional
   https configuration can be configured via `client_options`.
- `database` - *(optional)*: the database/tenant to use
- `query_options` - *(optional)*: global query options for all queries made from the connection. See [**query_options**](../reference/options.md#queryoptions)
- `client_options` - *(optional)*: httpx client options for all queries made from the connection. See [**client_options**](../reference/options.md#clientoptions)

---
## [Cursors](../reference/cursor.md)
Cursors are used for executing queries, scrolling through the result set, and fetching rows from the result set.  A
cursor object can be constructed directly by passing a connection, however most of the time you will use the `cursor`
factory function on `pinot_connect.Connection` or `pinot_connect.AsyncConnection`.

Cursors support passing row factories.  See the [row factory docs](row_factories.md) for detailed examples.

The below examples assumes you already have a connection instance.
!!! example
    === "sync"
        ```py title="Using a Cursor"
        from pinot_connect.rows import dict_row
    
        # use it as a context manager, cleans up resources when block exits
        with conn.cursor(row_factory=dict_row) as cursor:
            cursor.execute("select * from airlineStats")
            # fetch a single row from the result set
            row = cursor.fetchone()  
            # fetch the next ten rows from the result set
            next_ten_rows = cursor.fetchmany(10) 
            # fetch remaining rows
            remaining_rows = cursor.fetchall() 
    
        # or call it and close it later
        cursor = conn.cursor(row_factory=dict_row)
        # do stuff
        cursor.close()
        ```
    === "async"
        ```py title="Using an AsyncCursor"
        async def main(conn: pinot_connect.AsyncConnection):
            # use it as an async context manager, cleans up rsesources when block exits
            async with conn.cursor(row_factory=dict_row):
                await cursor.execute("select * from airlineStats")
                # fetch a single row from the result set
                rows = await cursor.fetchone()  
                # fetch the next ten rows from the result seet
                next_ten_rows = await cursor.fetchmany(10) 
                 # fetch remaining rows
                remaining_rows = await cursor.fetchall()

            # or await it and close it later
            cursor = await conn.cursor(row_factory=dict_row)
            # do stuff
            await cursor.close()
        ```

- Cursors, like connections, can be reused. Executing a new query automatically clears the cursor’s state, allowing you 
  to fetch results from the latest execution.
- Cursors are NOT thread-safe or task-safe. Sharing them across threads or async tasks can cause race conditions. Each 
  thread or task should create and manage its own cursor.
- Creating a cursor is lightweight, so creating a new one when needed is recommended.

Cursor factories take the following arguments:
- `query_options` - *(optional)*: query options to be used by cursor, overrides any options set at connection level.  See [**query_options**](../reference/options.md#queryoptions).
- `row_factory` - *(optional)*: RowFactory type to use to build rows fetched from cursor, defaults to returning tuples.

### Parameters
Pinot does not support server-side parameter binding, but `pinot_connect` simplifies query composition while ensuring type 
safety by handling client-side parameter binding. It converts Python types into Pinot-compatible formats and ensures 
they are safely serialized to JSON for query requests.

`pinot_connect` supports the `pyformat` paramstyle, allowing:

- Named parameters: Use `%(name)s`, with parameters passed as a dict
- Positional parameters: Use `%s`, with parameters passed as a list or tuple

```py title="select * from airlineStats where Airtime > 200 and Carrier = 'AA'"
cursor.execute(
    "select * from airlineStats where AirTime > %s and Carrier = %s", 
    (200, "AA")
)
```

Below is a table of input types and how they will be interpolated into the query string:

| Input Type                | Example Input                                  | Output Example                             | Notes                                                  |
|---------------------------|------------------------------------------------|--------------------------------------------|--------------------------------------------------------|
| `str`                     | `"hello"`                                      | `"'hello'"`                                | Escapes single quotes within strings.                  |
| `str` (with single quote) | `"O'Reilly"`                                   | `"'O''Reilly'"`                            | Escapes single quotes by doubling them.                |
| `bool`                    | `True` / `False`                               | `"TRUE"` / `"FALSE"`                       | Converts booleans to uppercase SQL literals.           |
| `int`                     | `42`                                           | `"42"`                                     | Converts integers to strings.                          |
| `float`                   | `3.14`                                         | `"3.14"`                                   | Converts floats to strings.                            |
| `decimal.Decimal`         | `Decimal('10.5')`                              | `"10.5"`                                   | Converts Decimal values to strings.                    |
| `datetime.date`           | `date(2025, 2, 24)`                            | `"'2025-02-24'"`                           | Uses ISO format inside single quotes.                  |
| `datetime.datetime`       | `datetime(2025, 2, 24, 14, 30, 0)`             | `"'2025-02-24T14:30:00'"`                  | Uses ISO format inside single quotes.                  |
| `list`, `tuple`, `set`    | `[1, 'abc', None]`                             | `"(1, 'abc', NULL)"`                       | Recursively applies escaping for each element.         |
| `NoneType`                | `None`                                         | `"NULL"`                                   | Converts `None` to SQL `NULL`.                         |
| `dict`                    | `{"key": "value"}`                             | `"'{"key":"value"}'"`                      | JSON-encodes the dictionary and escapes single quotes. |
| `uuid.UUID`               | `UUID("12345678-1234-5678-1234-567812345678")` | `"'12345678-1234-5678-1234-567812345678'"` | Converts UUID to string and wraps in single quotes.    |
| Unsupported types         | `object()`                                     | Raises `ProgrammingError`                  | Only supported types are listed above.                 |


#### `cursor.mogrify` 
`cursor.mogrify` can be used for binding a query once and reusing it in subsequent execute calls, but is also useful for
debugging
```py title="Using cursor.mogrify"
bound_op = cursor.mogrify(
    "select * from airlineStats where AirTime > %s", 
    (200,)
)
print(bound_op)  # "select * from airlineStats where AirTime > 200
```

### Converting types
When querying data, `pinot_connect` will convert Pinot types into python types where it can.  

!!! warning
    JSON columns are both STRING type and serialized as strings in json when querying Pinot.  Because of this, it is
    impossible to know which columns are JSON without using a row_factory.  If you want your JSON columns deserialized
    into python dictionaries, you should use the `dict_row_load_json_fields` row factory, or write your own row factory.

| Pinot Type    | Python Type         | Notes                                                                                                       |
|---------------|---------------------|-------------------------------------------------------------------------------------------------------------|
| `INT`         | `int`               |                                                                                                             |
| `LONG`        | `int`               |                                                                                                             |
| `FLOAT`       | `float`             |                                                                                                             |
| `DOUBLE`      | `float`             |                                                                                                             |
| `BIG_DECIMAL` | `decimal.Decimal`   |                                                                                                             |
| `BOOLEAN`     | `bool`              |                                                                                                             |
| `TIMESTAMP`   | `datetime.datetime` | uses the `ciso8601` package                                                                                 |
| `STRING`      | `str`               |                                                                                                             |
| `JSON`        | `str`               | Can be loaded with `dict_row_load_json_fields`                                                              |
| `BYTES`       | `str`               | Pinot returns bytes columns as encoded strings, so for performance reasons `pinot_connect` leaves those untouched |