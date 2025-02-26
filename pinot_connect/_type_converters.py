from __future__ import annotations

import decimal
import typing as t

import ciso8601

_CONVERTER_MAP: t.Final[dict[str, t.Callable[[t.Any], t.Any]]] = {
    "TIMESTAMP": ciso8601.parse_datetime,  # https://www.iso.org/iso-8601-date-and-time-format.html
    "BIG_DECIMAL": decimal.Decimal,
}


def build_converters(types: list[str]) -> dict[int, t.Callable[[t.Any], t.Any]]:
    return {index: _CONVERTER_MAP[dt] for index, dt in enumerate(types) if dt in _CONVERTER_MAP}
