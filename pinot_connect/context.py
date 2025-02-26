from __future__ import annotations

import typing as t
from types import TracebackType

_TObj = t.TypeVar("_TObj")

__all__ = ["CoroContextManager"]


class CoroContextManager(t.Coroutine[t.Any, t.Any, _TObj], t.Generic[_TObj]):
    """Simple object that allows an async function to be awaited directly or called using `async with func(...)`.

    Prevents having to write `async with await func(...)`
    """

    __slots__ = ("_coro", "_obj")

    def __init__(
        self,
        coro: t.Coroutine[t.Any, t.Any, _TObj],
    ):
        self._coro = coro
        self._obj: _TObj | None = None  # type: ignore[assignment]

    def send(self, value: t.Any) -> t.Any:  # pragma: no cover
        return self._coro.send(value)

    def throw(  # type: ignore
        self,
        typ: t.Type[BaseException],
        val: BaseException | object | None = None,
        tb: TracebackType | None = None,
    ) -> t.Any:  # pragma: no cover
        if val is None:
            return self._coro.throw(typ)
        if tb is None:
            return self._coro.throw(typ, val)
        return self._coro.throw(typ, val, tb)

    def close(self) -> None:  # pragma: no cover
        self._coro.close()

    def __await__(self) -> t.Generator[t.Any, None, _TObj]:  # pragma: no cover
        return self._coro.__await__()

    async def __aenter__(self) -> _TObj:
        if self._obj is None:
            self._obj = await self._coro
        if hasattr(self._obj, "__aenter__"):
            await self._obj.__aenter__()  # type: ignore
        assert self._obj
        return self._obj

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self._obj, "__aexit__"):
            await self._obj.__aexit__(exc_type, exc_val, exc_tb)  # type: ignore
