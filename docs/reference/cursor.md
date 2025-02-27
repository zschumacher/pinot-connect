<a id="pinot_connect.cursor"></a>

# pinot\_connect.cursor

<a id="pinot_connect.cursor.QueryStatistics"></a>

---
## QueryStatistics

```python
class QueryStatistics(t.TypedDict)
```

TypedDict for exposing query statistics for the last executed query

This exposes relevant statistics and metrics from the query execution reported
by the Pinot broker, including server-side performance, pruning details, and
total rows/documents processed.

**Attributes**:

- `brokerId` - The ID of the broker that executed this query.
- `brokerReduceTimeMs` - The time taken by the broker to reduce the results from servers, expressed in milliseconds.
- `explainPlanNumEmptyFilterSegments` - Number of segments skipped due to empty filter matches in the explain plan.
- `explainPlanNumMatchAllFilterSegments` - Number of segments where all rows matched due to 'match-all' filter in the explain plan.
- `maxRowsInJoinReached` - Indicates if the query processing hit the maximum number of rows allowed in a join operation.
- `maxRowsInOperator` - The maximum number of rows processed by any operator during query execution.
- `maxRowsInWindowReached` - Indicates if the maximum number of rows were hit in any window function during execution.
- `minConsumingFreshnessTimeMs` - The minimum freshness time in milliseconds of consuming (real-time) segments.
- `numConsumingSegmentsMatched` - The number of consuming (real-time) segments that matched the query criteria.
- `numConsumingSegmentsProcessed` - The number of consuming (real-time) segments that were processed during query execution.
- `numConsumingSegmentsQueried` - The number of consuming (real-time) segments queried during the execution.
- `numDocsScanned` - The total number of documents (rows) scanned in the query.
- `numEntriesScannedInFilter` - The total number of entries scanned by filter operations during the query.
- `numEntriesScannedPostFilter` - The total number of entries scanned after applying filter operations.
- `numGroupsLimitReached` - Indicates if the limit on the number of groups in the GROUP BY clause was reached.
- `numRowsResultSet` - The total number of rows returned in the query result set.
- `numSegmentsMatched` - The total number of segments that matched the query criteria.
- `numSegmentsProcessed` - The total number of segments processed by the servers during query processing.
- `numSegmentsPrunedByBroker` - The number of segments that were pruned (skipped) by the broker.
- `numSegmentsPrunedByLimit` - The number of segments pruned due to query limits (e.g., TOP N queries).
- `numSegmentsPrunedByServer` - The number of segments pruned by the servers during query execution.
- `numSegmentsPrunedByValue` - The number of segments pruned based on the value range (e.g., partitioning or pruning on primary keys).
- `numSegmentsPrunedInvalid` - The number of invalid or unnecessary segments pruned by the broker or server.
- `numSegmentsQueried` - The number of segments queried during the execution.
- `numServersQueried` - The number of servers queried by the broker for this request.
- `numServersResponded` - The number of servers that successfully responded with query results.
- `offlineResponseSerializationCpuTimeNs` - CPU time spent in serializing offline segment responses, in nanoseconds.
- `offlineSystemActivitiesCpuTimeNs` - Total CPU time spent in system activities related to offline segments, in nanoseconds.
- `offlineThreadCpuTimeNs` - Total thread CPU time spent in processing offline segments, in nanoseconds.
- `offlineTotalCpuTimeNs` - Total CPU time including query processing for offline segments, in nanoseconds.
- `partialResult` - Indicates if the result is partial (e.g., due to query timeouts or server issues).
- `realtimeResponseSerializationCpuTimeNs` - CPU time spent serializing real-time segment responses, in nanoseconds.
- `realtimeSystemActivitiesCpuTimeNs` - Total CPU time spent in system activities for real-time segments, in nanoseconds.
- `realtimeThreadCpuTimeNs` - Total thread CPU time spent in processing real-time segments, in nanoseconds.
- `realtimeTotalCpuTimeNs` - Total CPU time including query processing for real-time segments, in nanoseconds.
- `requestId` - The unique identifier for the query request.
- `segmentStatistics` - A list of segment-level statistics for query execution.
- `stageStats` - A dictionary containing stage-specific statistics for multi-stage queries.
- `stateStats` - A dictionary containing state-specific statistics for query execution.
- `tablesQueried` - A list of table names that were queried.
- `timeUsedMs` - The total time taken to execute the query, in milliseconds.
- `totalDocs` - The total number of documents in the queried segments.
- `traceInfo` - A dictionary containing tracing information for the query execution.

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

<a id="pinot_connect.cursor.BaseCursor.query_statistics"></a>

#### query\_statistics

```python
@property
def query_statistics() -> QueryStatistics | None
```

Statistics about the last executed query

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

