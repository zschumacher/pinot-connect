from pinot_connect.options import QUERY_OPTION_NOT_SET
from pinot_connect.options import QueryOptions


class TestQueryOptions:
    def test_asdict_all_notset(self):
        options = QueryOptions()
        assert options.asdict() == {
            "timeoutMs": QUERY_OPTION_NOT_SET,
            "enableNullHandling": QUERY_OPTION_NOT_SET,
            "explainPlanVerbose": QUERY_OPTION_NOT_SET,
            "useMultiStageEngine": QUERY_OPTION_NOT_SET,
            "maxExecutionThreads": QUERY_OPTION_NOT_SET,
            "numReplicaGroupsToQuery": QUERY_OPTION_NOT_SET,
            "minSegmentGroupTrimSize": QUERY_OPTION_NOT_SET,
            "minServerGroupTrimSize": QUERY_OPTION_NOT_SET,
            "serverReturnFinalResult": QUERY_OPTION_NOT_SET,
            "serverReturnFinalResultKeyUnpartitioned": QUERY_OPTION_NOT_SET,
            "skipIndexes": QUERY_OPTION_NOT_SET,
            "skipUpsert": QUERY_OPTION_NOT_SET,
            "useStarTree": QUERY_OPTION_NOT_SET,
            "AndScanReordering": QUERY_OPTION_NOT_SET,
            "maxRowsInJoin": QUERY_OPTION_NOT_SET,
            "inPredicatePreSorted": QUERY_OPTION_NOT_SET,
            "inPredicateLookupAlgorithm": QUERY_OPTION_NOT_SET,
            "maxServerResponseSizeBytes": QUERY_OPTION_NOT_SET,
            "maxQueryResponseSizeBytes": QUERY_OPTION_NOT_SET,
            "filteredAggregationsSkipEmptyGroup": QUERY_OPTION_NOT_SET,
        }

    def test_asdict_some_values_set(self):
        options = QueryOptions(timeout_ms=5000, enable_null_handling=True)
        assert options.asdict()["timeoutMs"] == 5000
        assert options.asdict()["enableNullHandling"] is True

    def test_to_kv_pair_all_notset(self):
        options = QueryOptions()
        assert QueryOptions.to_kv_pair(options.asdict()) == ""

    def test_to_kv_pair_some_values_set(self):
        options = QueryOptions(timeout_ms=5000, enable_null_handling=True, explain_plan_verbose=False)
        kv_pair = QueryOptions.to_kv_pair(options.asdict())
        assert "timeoutMs=5000" in kv_pair
        assert "enableNullHandling=true" in kv_pair
        assert "explainPlanVerbose=false" in kv_pair
        assert kv_pair.count(";") == 2  # Ensure key-value pairs are properly separated by ';'
