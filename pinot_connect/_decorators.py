import functools
import typing as t

from typing_extensions import ParamSpec

from .exceptions import ProgrammingError

_P = ParamSpec("_P")
_T = t.TypeVar("_T")


def check_cursor_open(f: t.Callable[_P, _T]) -> t.Callable[_P, _T]:
    @functools.wraps(f)
    def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        cursor = args[0]  # type: ignore
        if cursor.closed:  # type: ignore[attr-defined]
            raise ProgrammingError(f"Operation failed: Cannot call {f.__name__} on closed cursor.")
        return f(*args, **kwargs)

    return wrapper


def acheck_cursor_open(f: t.Callable[_P, t.Awaitable[_T]]) -> t.Callable[_P, t.Awaitable[_T]]:
    @functools.wraps(f)
    async def wrapper(*args: _P.args, **kwargs: _P.kwargs) -> _T:
        cursor = args[0]  # type: ignore
        if cursor.closed:  # type: ignore[attr-defined]
            raise ProgrammingError(f"Operation failed: Cannot call {f.__name__} on closed cursor.")
        return await f(*args, **kwargs)

    return wrapper
