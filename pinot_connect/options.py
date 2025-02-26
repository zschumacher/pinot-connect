from __future__ import annotations

import dataclasses
import ssl
import typing as t
from dataclasses import dataclass

import httpx
from httpx import _types as httpx_types

__all__ = [
    "QueryOption",
    "QueryOptions",
    "QUERY_OPTION_NOT_SET",
    "ClientOptions",
    "RequestOptions",
    "DEFAULT_REQUEST_TIMEOUT",
    "DEFAULT_CONNECTION_LIMITS",
    "DEFAULT_MAX_REDIRECTS",
]

DEFAULT_REQUEST_TIMEOUT: t.Final[httpx.Timeout] = httpx.Timeout(5.0)
DEFAULT_CONNECTION_LIMITS: t.Final[httpx.Limits] = httpx.Limits(max_connections=100, max_keepalive_connections=20)
DEFAULT_MAX_REDIRECTS: t.Final[int] = 20


class _NotSet:
    ...


QUERY_OPTION_NOT_SET = _NotSet()

_OptionType = t.TypeVar("_OptionType")
QueryOption = t.Union[_OptionType, _NotSet]


@dataclass()
class QueryOptions:
    """Helper object for constructing [query options for pinot](https://docs.pinot.apache.org/users/user-guide-query/query-options)

    All values are optional and default to being not set (will not be included in passed options)

    Attributes:
        timeout_ms: timeout of query in milliseconds
        enable_null_handling: enable advanced null handling
        explain_plan_verbose: return verbose result for `EXPLAIN` query
        use_multi_stage_engine: e multi-stage engine for executing query
        max_execution_threads: Maximum threads to use to execute the query
        num_replica_groups_to_query: When replica-group based routing is enabled, use it to query multiple replica-groups
        min_segment_group_trim_size: Minimum groups to keep when trimming groups at the segment level for group-by queries
        min_server_group_trim_size: Minimum groups to keep when trimming groups at the server level for group-by queries
        server_return_final_result: For aggregation and group-by queries, ask servers to directly return final results
            instead of intermediate results for aggregation
        server_return_final_result_key_unpartitioned: For group-by queries, ask servers to directly return final results
            instead of intermediate results for aggregations
        skip_indexes: Which indexes to skip usage of (i.e. scan instead), per-column
        skip_upsert: For upsert-enabled table, skip the effect of upsert and query all the records
        use_star_tree: Useful to debug the star-tree index
        and_scan_reordering: [See description](https://docs.pinot.apache.org/operators/tutorials/performance-optimization-configurations)
        max_rows_in_join: Configure maximum rows allowed in a join operation
        in_predicate_pre_sorted: (Only apply to STRING columns) Indicates that the values in the IN clause is already
            sorted, so that Pinot doesn't need to sort them again at query time
        in_predicate_lookup_algorithm: The algorithm to use to look up the dictionary ids for the IN clause values
        max_server_response_size_bytes: Long value config indicating the maximum length of the serialized response per
            server for a query
        max_query_response_size_bytes: Long value config indicating the maximum serialized response size across all
            servers for a query
        filtered_aggregations_skip_empty_groups: This config can be set to true to avoid computing all the groups in a
            group by query with only filtered aggregations (and no non-filtered aggregations)
    """

    timeout_ms: QueryOption[int] = QUERY_OPTION_NOT_SET
    enable_null_handling: QueryOption[bool] = QUERY_OPTION_NOT_SET
    explain_plan_verbose: QueryOption[bool] = QUERY_OPTION_NOT_SET
    use_multi_stage_engine: QueryOption[bool] = QUERY_OPTION_NOT_SET
    max_execution_threads: QueryOption[int] = QUERY_OPTION_NOT_SET
    num_replica_groups_to_query: QueryOption[int] = QUERY_OPTION_NOT_SET
    min_segment_group_trim_size: QueryOption[int] = QUERY_OPTION_NOT_SET
    min_server_group_trim_size: QueryOption[int] = QUERY_OPTION_NOT_SET
    server_return_final_result: QueryOption[bool] = QUERY_OPTION_NOT_SET
    server_return_final_result_key_unpartitioned: QueryOption[bool] = QUERY_OPTION_NOT_SET
    skip_indexes: QueryOption[str] = QUERY_OPTION_NOT_SET
    skip_upsert: QueryOption[bool] = QUERY_OPTION_NOT_SET
    use_star_tree: QueryOption[bool] = QUERY_OPTION_NOT_SET
    and_scan_reordering: QueryOption[bool] = QUERY_OPTION_NOT_SET
    max_rows_in_join: QueryOption[int] = QUERY_OPTION_NOT_SET
    in_predicate_pre_sorted: QueryOption[bool] = QUERY_OPTION_NOT_SET
    in_predicate_lookup_algorithm: QueryOption[
        t.Literal["DIVIDE_BINARY_SEARCH", "SCAN", "PLAIN_BINARY_SEARCH"]
    ] = QUERY_OPTION_NOT_SET
    max_server_response_size_bytes: QueryOption[int] = QUERY_OPTION_NOT_SET
    max_query_response_size_bytes: QueryOption[int] = QUERY_OPTION_NOT_SET
    filtered_aggregations_skip_empty_groups: QueryOption[bool] = QUERY_OPTION_NOT_SET

    def asdict(self) -> dict:
        return dict(
            timeoutMs=self.timeout_ms,
            enableNullHandling=self.enable_null_handling,
            explainPlanVerbose=self.explain_plan_verbose,
            useMultiStageEngine=self.use_multi_stage_engine,
            maxExecutionThreads=self.max_execution_threads,
            numReplicaGroupsToQuery=self.num_replica_groups_to_query,
            minSegmentGroupTrimSize=self.min_segment_group_trim_size,
            minServerGroupTrimSize=self.min_server_group_trim_size,
            serverReturnFinalResult=self.server_return_final_result,
            serverReturnFinalResultKeyUnpartitioned=self.server_return_final_result_key_unpartitioned,
            skipIndexes=self.skip_indexes,
            skipUpsert=self.skip_upsert,
            useStarTree=self.use_star_tree,
            AndScanReordering=self.and_scan_reordering,
            maxRowsInJoin=self.max_rows_in_join,
            inPredicatePreSorted=self.in_predicate_pre_sorted,
            inPredicateLookupAlgorithm=self.in_predicate_lookup_algorithm,
            maxServerResponseSizeBytes=self.max_server_response_size_bytes,
            maxQueryResponseSizeBytes=self.max_query_response_size_bytes,
            filteredAggregationsSkipEmptyGroup=self.filtered_aggregations_skip_empty_groups,
        )

    @classmethod
    def merge(cls, parent: QueryOptions, child: QueryOptions) -> QueryOptions:
        return dataclasses.replace(parent, **vars(child))

    @classmethod
    def to_kv_pair(cls, d: dict) -> str:
        """Pinot's servers expect query options to be sent as 'option1=value;option2=value"""
        return ";".join(
            f"{k}={v if v not in {True, False} else str(v).lower()}" for k, v in d.items() if v != QUERY_OPTION_NOT_SET
        )


@dataclasses.dataclass()
class ClientOptions:
    """Options too pass on to the underlying httpx Client/AsyncClient constructor

    Attributes:
        cookies: *(optional)* Dictionary of Cookie items to include when sending requests
        verify: *(optional)* Either `True` to use an SSL context with the default CA bundle, `False` to disable
            verification, or an instance of `ssl.SSLContext` to use a custom context
        cert: *(optional)* Path(s) to the SSL certificate file(s)
        trust_env: *(optional)* Enables or disables usage of environment variables for configuration
        proxy:  *(optional)* A proxy URL where all the traffic should be routed
        timeout: *(optional)* The timeout configuration to use when sending request, all in seconds
        follow_redirects: *(optional)* Whether to follow redirects when sending request.  Default: `true`.
        limits: *(optional)* The limits configuration to use.
        max_redirects: *(optional)* The maximum number of redirect responses that should be followed request URLs
        transport: *(optional)* A transport class to use for sending requests over the network
        event_hooks: *(optional)* A list of hooks to when either request has been prepared or reponse has been fetched
        default_encoding: *(optional)* The default encoding to use for decoding response text, if no charset information
            is included in a response Content-Type header. Set to a callable for automatic character set detection.
            Default: "utf-8".
    """

    cookies: httpx_types.CookieTypes | None = None
    verify: ssl.SSLContext | str | bool = True
    cert: httpx_types.CertTypes | None = None
    trust_env: bool = True
    proxy: httpx_types.ProxyTypes | None = None
    timeout: httpx_types.TimeoutTypes = DEFAULT_REQUEST_TIMEOUT
    follow_redirects: bool = False
    limits: httpx.Limits = DEFAULT_CONNECTION_LIMITS
    max_redirects: int | None = DEFAULT_MAX_REDIRECTS
    transport: httpx.BaseTransport | None = None
    event_hooks: t.Mapping[str, list[t.Callable[..., t.Any]]] | None = None
    default_encoding: t.Callable[[bytes], str] | str = "utf-8"


@dataclasses.dataclass()
class RequestOptions:
    """Options to pass to the actual HTTP request via execute methods

    Attributes:
        cookies: *(optional)* Dictionary of Cookie items to include when sending requests
        timeout: *(optional)* The timeout configuration to use when sending request, all in seconds
        extensions: *(optional)* Optional dictionary for low-level request customizations
    """

    cookies: httpx_types.CookieTypes | None = None
    timeout: httpx_types.TimeoutTypes | None = None
    extensions: httpx_types.RequestExtensions | None = None
