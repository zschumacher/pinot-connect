# Advanced Configuration Options
*pinot_connect* has two helper objects for advanced configuration of the `httx` client as well as Apache Pinot query options

---
## [QueryOptions](../reference/options.md#queryoptions)
Helper object for building Apache Pinot 
[**query options**](https://docs.pinot.apache.org/users/user-guide-query/query-options).

Query options can be set at different levels: **connection**, **cursor**, and **execute**.

- `QueryOptions` set on the connection serve as defaults.
- `QueryOptions` set on the cursor override those from the connection but inherit any not explicitly set.
- `QueryOptions` set on execute override those from the cursor but inherit any not explicitly set.
- Any unset option will use the Pinot server default

```python title="Using QueryOptions"
import pinot_connect

query = "select * from airlineStats limit 10"

# set default query timeout on connection to 500ms
with pinot_connect.connect("localhost", query_options=pinot_connect.QueryOptions(timeout_ms=500)) as conn:
    # cursor default is 500, inherited from connection
    with conn.cursor() as cursor:  
        # uses timeout of 500ms, inherited from cursor, which inherited from connection
        cursor.execute(query)
        # use a timeout of 100ms for this query only
        cursor.execute(query, query_options=pinot_connect.QueryOptions(timeout_ms=100))
        
    # now the default for this cursor will be 150, overrides connection default of 500ms
    with conn.cursor(query_options=pinot_connect.QueryOptions(timeout_ms=150)): 
        # uses timeout of 150ms, inherited from cursor
        cursor.execute(query)
        # use a timeout of 50ms for this query only
        cursor.execute(query, query_options=pinot_connect.QueryOptions(timeout_ms=50))
```
!!! note
    `timeout_ms` is only a measure of actual query execution, which DOES NOT include network latency.  To set a timeout
    on execution time + network latency, see [`ClientOptions`](#clientoptions) below.

---
## [ClientOptions](../reference/options.md#clientoptions)
Helper object for building keyword arguments to pass from  `pinot_connect.Connection` -> `httpx.Client` and `AsyncConnection` 
-> `httpx.AsyncClient`.  Because queries are emitted to Apache Pinot via http/https, this object allows you to customize
additional settings for all requests made from the `pinot_connect.Connection`/`pinot_connect.AsyncConnection` instance(s).

!!! note
    `timeout` in `httpx` accepts seconds, but takes a float value.  This is different than pinot's options, which takes
    `timeout_ms` as milliseconds.

```python title="Using ClientOptions"
import pinot_connect

query = "select * from airlineStats limit 10"

# set default request timeout on all requests from connection to 2s
with pinot_connect.connect("localhost", client_options=pinot_connect.ClientOptions(timeout=2)) as conn:
    with conn.cursor() as cursor:  
        cursor.execute(query)
```

## [RequestOptions](../reference/options.md#requestoptions)
Helper object for setting timeouts, cookies or extensions for a single request/query.  The passed timeout and/or cookies
would override anything set on the connection and/or cursor.

```python title="Using RequestOptions"
import pinot_connect

query = "select * from airlineStats limit 10"

# set default request timeout on all requests from connection to 2s
with pinot_connect.connect("localhost", client_options=pinot_connect.ClientOptions(timeout=2.0)) as conn:
    with conn.cursor() as cursor:  
        # extend timeout for this query only
        cursor.execute(query, request_options=pinot_connect.RequestOptions(timeout=5.0))
        # uses timeout of 2.0 from connection
        cursor.execute(query)
```