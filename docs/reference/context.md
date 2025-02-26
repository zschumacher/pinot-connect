<a id="pinot_connect.context"></a>

# pinot\_connect.context

<a id="pinot_connect.context.CoroContextManager"></a>

---
## CoroContextManager

```python
class CoroContextManager(t.Coroutine[t.Any, t.Any, _TObj], t.Generic[_TObj])
```

Simple object that allows an async function to be awaited directly or called using `async with func(...)`.

Prevents having to write `async with await func(...)`

