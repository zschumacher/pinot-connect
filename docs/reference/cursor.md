<a id="pinot_connect.cursor"></a>

# pinot\_connect.cursor

<a id="pinot_connect.cursor.BaseCursor"></a>

---
## BaseCursor

```python
class BaseCursor(t.Generic[_ConnectionType, RowType])
```

<a id="pinot_connect.cursor.BaseCursor.description"></a>

#### description

```python
@property
def description() -> list[Column] | None
```

Description of query result

Only name and type code (index 0 and 1) will ever be populated for this
implementation

<a id="pinot_connect.cursor.BaseCursor.connection"></a>

#### connection

```python
@property
def connection() -> _ConnectionType
```

Pointer to the connection used to create this cursor

<a id="pinot_connect.cursor.BaseCursor.rownumber"></a>

#### rownumber

```python
@property
def rownumber() -> int | None
```

Current position of cursor

<a id="pinot_connect.cursor.BaseCursor.rowcount"></a>

#### rowcount

```python
@property
def rowcount() -> int | None
```

Number of rows returned by last executed query

<a id="pinot_connect.cursor.BaseCursor.closed"></a>

#### closed

```python
@property
def closed() -> bool
```

`True` if the cursor is closed

<a id="pinot_connect.cursor.BaseCursor.arraysize"></a>

#### arraysize

```python
@property
def arraysize() -> int
```

Number of rows to fetch with fetchmany if no size is specified in the method call

<a id="pinot_connect.cursor.BaseCursor.query"></a>

#### query

```python
@property
def query() -> str | None
```

Last executed query

<a id="pinot_connect.cursor.BaseCursor.mogrify"></a>

#### mogrify

```python
def mogrify(operation: str, params: dict | tuple | list | None = None) -> str
```

Take an operation and params and return the operation after param binding

<a id="pinot_connect.cursor.Cursor"></a>

---
## Cursor

```python
class Cursor(BaseCursor["Connection", RowType])
```

<a id="pinot_connect.cursor.Cursor.scroll"></a>

#### scroll

```python
@check_cursor_open
def scroll(value: int,
           *,
           mode: t.Literal["relative", "absolute"] = "relative") -> None
```

Move the cursor in the result set to a new position using the mode.

If mode=`relative` (default), treat the passed value as an offset relative to the current position in the result
set. If mode=`absolute`, move to the passed position.

**Arguments**:

- `value` - The offset if in `relative` mode; the target position if in `absolute` mode
- `mode` - *(optional)* determines the model to use for the scroll.  Default: `relative`

<a id="pinot_connect.cursor.Cursor.execute"></a>

#### execute

```python
@check_cursor_open
def execute(operation: str,
            params: dict | tuple | list | None = None,
            *,
            query_options: QueryOptions | None = None,
            request_options: RequestOptions | None = None) -> httpx.Response
```

Execute a query against the *Pinot* broker

The query returns the `httpx.Response` from the request, which you normally will not need; however,
it may be useful for debugging.

**Arguments**:

- `operation` - the sql operation to send to the broker
- `params` - *(optional)* sql params to bind to the operation
- `query_options` - *(optional)* query options that override what is set on cursor/connection
- `request_options` - *(optional)* request options to use for this specific query.  Can override timeout and
  cookies from cursor/connection

<a id="pinot_connect.cursor.Cursor.fetchone"></a>

#### fetchone

```python
@check_cursor_open
def fetchone() -> RowType | None
```

Fetch the next record from the current result set or `None` if exhausted

uses passed `row_factory` to cursor to determine `RowType` of returned row

<a id="pinot_connect.cursor.Cursor.fetchmany"></a>

#### fetchmany

```python
@check_cursor_open
def fetchmany(size: int | None = None) -> list[RowType]
```

Fetch the next size records from the current result set.  If size is not passed, the value
of the `arraysize` property will be used instead.

Uses passed `row_factory` to cursor to determine `RowType` of returned rows.

> This method can return fewer records than requested.  For example, if a size of 3 is passed, but the result
> set only has two records remaining, the two records will be returned only.

**Arguments**:

- `size` - *(optional)* number of records to fetch - if not passed, will use arraysize property instead

<a id="pinot_connect.cursor.Cursor.fetchall"></a>

#### fetchall

```python
@check_cursor_open
def fetchall() -> list[RowType]
```

Fetch all remaining records from the current result set.  Returns empty list if no
records remaining or result set is empty.

Uses passed `row_factory` to cursor to determine `RowType` of returned rows.

<a id="pinot_connect.cursor.Cursor.close"></a>

#### close

```python
def close() -> None
```

Close cursor and cleanup resources

<a id="pinot_connect.cursor.AsyncCursor"></a>

---
## AsyncCursor

```python
class AsyncCursor(BaseCursor["AsyncConnection", RowType])
```

<a id="pinot_connect.cursor.AsyncCursor.scroll"></a>

#### scroll

```python
@acheck_cursor_open
async def scroll(value: int,
                 *,
                 mode: t.Literal["relative", "absolute"] = "relative") -> None
```

Move the cursor in the result set to a new position using the mode.

If mode=`relative` (default), treat the passed value as an offset relative to the current position in the result
set. If mode=`absolute`, move to the passed position.

**Arguments**:

- `value` - The offset if in `relative` mode; the target position if in `absolute` mode
- `mode` - *(optional)* determines the model to use for the scroll.  Default: `relative`

<a id="pinot_connect.cursor.AsyncCursor.execute"></a>

#### execute

```python
@acheck_cursor_open
async def execute(operation: str,
                  params: dict | tuple | list | None = None,
                  *,
                  query_options: QueryOptions | None = None) -> httpx.Response
```

Execute a query against the *Pinot* broker

The query returns the `httpx.Response` from the request, which you normally will not need; however,
it may be useful for debugging.

**Arguments**:

- `operation` - the sql operation to send to the broker
- `params` - *(optional)* sql params to bind to the operation
- `query_options` - *(optional)* query options that override what is set on cursor/connection

<a id="pinot_connect.cursor.AsyncCursor.fetchone"></a>

#### fetchone

```python
@acheck_cursor_open
async def fetchone() -> RowType | None
```

Fetch the next record from the current result set or `None` if exhausted

Uses passed `row_factory` to cursor to determine `RowType` of returned row

<a id="pinot_connect.cursor.AsyncCursor.fetchmany"></a>

#### fetchmany

```python
@acheck_cursor_open
async def fetchmany(size: int | None = None) -> list[RowType]
```

Fetch the next size records from the current result set.  If size is not passed, the value
of the `arraysize` property will be used instead.

Uses passed `row_factory` to cursor to determine `RowType` of returned rows.

> This method can return fewer records than requested.  For example, if a size of 3 is passed, but the result
> set only has two records remaining, the two records will be returned only.

**Arguments**:

- `size` - *(optional)* number of records to fetch - if not passed, will use arraysize property instead

<a id="pinot_connect.cursor.AsyncCursor.fetchall"></a>

#### fetchall

```python
@acheck_cursor_open
async def fetchall() -> list[RowType]
```

Fetch all remaining records from the current result set.  Returns empty list if no
records remaining or result set is empty.

Uses passed `row_factory` to cursor to determine `RowType` of returned rows.

<a id="pinot_connect.cursor.AsyncCursor.close"></a>

#### close

```python
async def close() -> None
```

Close cursor and cleanup resources

