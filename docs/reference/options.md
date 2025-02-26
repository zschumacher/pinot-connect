<a id="pinot_connect.options"></a>

# pinot\_connect.options

<a id="pinot_connect.options.QueryOptions"></a>

---
## QueryOptions

```python
@dataclass()
class QueryOptions()
```

Helper object for constructing [query options for pinot](https://docs.pinot.apache.org/users/user-guide-query/query-options)

All values are optional and default to being not set (will not be included in passed options)

**Attributes**:

- `timeout_ms` - timeout of query in milliseconds
- `enable_null_handling` - enable advanced null handling
- `explain_plan_verbose` - return verbose result for `EXPLAIN` query
- `use_multi_stage_engine` - e multi-stage engine for executing query
- `max_execution_threads` - Maximum threads to use to execute the query
- `num_replica_groups_to_query` - When replica-group based routing is enabled, use it to query multiple replica-groups
- `min_segment_group_trim_size` - Minimum groups to keep when trimming groups at the segment level for group-by queries
- `min_server_group_trim_size` - Minimum groups to keep when trimming groups at the server level for group-by queries
- `server_return_final_result` - For aggregation and group-by queries, ask servers to directly return final results
  instead of intermediate results for aggregation
- `server_return_final_result_key_unpartitioned` - For group-by queries, ask servers to directly return final results
  instead of intermediate results for aggregations
- `skip_indexes` - Which indexes to skip usage of (i.e. scan instead), per-column
- `skip_upsert` - For upsert-enabled table, skip the effect of upsert and query all the records
- `use_star_tree` - Useful to debug the star-tree index
- `and_scan_reordering` - [See description](https://docs.pinot.apache.org/operators/tutorials/performance-optimization-configurations)
- `max_rows_in_join` - Configure maximum rows allowed in a join operation
- `in_predicate_pre_sorted` - (Only apply to STRING columns) Indicates that the values in the IN clause is already
  sorted, so that Pinot doesn't need to sort them again at query time
- `in_predicate_lookup_algorithm` - The algorithm to use to look up the dictionary ids for the IN clause values
- `max_server_response_size_bytes` - Long value config indicating the maximum length of the serialized response per
  server for a query
- `max_query_response_size_bytes` - Long value config indicating the maximum serialized response size across all
  servers for a query
- `filtered_aggregations_skip_empty_groups` - This config can be set to true to avoid computing all the groups in a
  group by query with only filtered aggregations (and no non-filtered aggregations)

<a id="pinot_connect.options.QueryOptions.to_kv_pair"></a>

#### to\_kv\_pair

```python
@classmethod
def to_kv_pair(cls, d: dict) -> str
```

Pinot's servers expect query options to be sent as 'option1=value;option2=value

<a id="pinot_connect.options.ClientOptions"></a>

---
## ClientOptions

```python
@dataclasses.dataclass()
class ClientOptions()
```

Options too pass on to the underlying httpx Client/AsyncClient constructor

**Attributes**:

- `cookies` - *(optional)* Dictionary of Cookie items to include when sending requests
- `verify` - *(optional)* Either `True` to use an SSL context with the default CA bundle, `False` to disable
  verification, or an instance of `ssl.SSLContext` to use a custom context
- `cert` - *(optional)* Path(s) to the SSL certificate file(s)
- `trust_env` - *(optional)* Enables or disables usage of environment variables for configuration
- `proxy` - *(optional)* A proxy URL where all the traffic should be routed
- `timeout` - *(optional)* The timeout configuration to use when sending request, all in seconds
- `follow_redirects` - *(optional)* Whether to follow redirects when sending request.  Default: `true`.
- `limits` - *(optional)* The limits configuration to use.
- `max_redirects` - *(optional)* The maximum number of redirect responses that should be followed request URLs
- `transport` - *(optional)* A transport class to use for sending requests over the network
- `event_hooks` - *(optional)* A list of hooks to when either request has been prepared or reponse has been fetched
- `default_encoding` - *(optional)* The default encoding to use for decoding response text, if no charset information
  is included in a response Content-Type header. Set to a callable for automatic character set detection.
- `Default` - "utf-8".

<a id="pinot_connect.options.RequestOptions"></a>

---
## RequestOptions

```python
@dataclasses.dataclass()
class RequestOptions()
```

Options to pass to the actual HTTP request via execute methods

**Attributes**:

- `cookies` - *(optional)* Dictionary of Cookie items to include when sending requests
- `timeout` - *(optional)* The timeout configuration to use when sending request, all in seconds
- `extensions` - *(optional)* Optional dictionary for low-level request customizations

