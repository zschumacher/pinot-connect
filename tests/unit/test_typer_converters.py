import decimal

import ciso8601

from pinot_connect._type_converters import build_converters


def test_build_converters():
    columns = ["STRING", "TIMESTAMP", "BIG_DECIMAL", "INT"]
    assert build_converters(columns) == {1: ciso8601.parse_datetime, 2: decimal.Decimal}
