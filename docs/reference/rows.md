<a id="pinot_connect.rows"></a>

# pinot\_connect.rows

<a id="pinot_connect.rows.RowMaker"></a>

---
## RowMaker

```python
class RowMaker(t.Protocol[RowType])
```

Protocol for a function that takes a list of values (a row) returned from the query and returns any RowType
object

<a id="pinot_connect.rows.RowFactory"></a>

---
## RowFactory

```python
class RowFactory(t.Protocol[RowType])
```

Protocol for a factory method that returns a RowMaker.  The method takes a description (from a cursor) which
is often useful for building dictionaries for usage or for passing into other objects as kwargs

<a id="pinot_connect.rows.tuple_row"></a>

---
#### tuple\_row

```python
def tuple_row(description: list["Column"]) -> RowMaker[tuple]
```

RowFactory that returns a tuple constructor to convert lis of values to tuple of values

Returns: RowMaker[tuple[t.Any, ...]]

<a id="pinot_connect.rows.list_row"></a>

---
#### list\_row

```python
def list_row(description: list["Column"]) -> RowMaker[list]
```

RowFactory that is a noop.  The data is returned as a list directly from the query, so this avoids any additional
data conversion.  This is not the default as most dbapis return tuple rows, but can easily be used when wanted.

<a id="pinot_connect.rows.dict_row"></a>

---
#### dict\_row

```python
def dict_row(description: list["Column"]) -> RowMaker[dict[str, t.Any]]
```

RowFactory that uses the description to get the column names and injects it into a row maker that converts
a row to a dictionary

<a id="pinot_connect.rows.dict_row_load_json_fields"></a>

---
#### dict\_row\_load\_json\_fields

```python
def dict_row_load_json_fields(*fields: str) -> RowFactory[dict[str, t.Any]]
```

pinot's query api always returns json fields as strings, with no indication that a field is actually a json field
one way would be to make an additional request to get the metadata of the schema, however the other way that does
not involve additional IO is specifying the lists of columns that should be loaded to python dictionaries and using
orjson to do that as efficiently as possible.  This function takes the field names and for those fields, then calls
orjson.loads on each of the corresponding values

<a id="pinot_connect.rows.kwargs_row"></a>

---
#### kwargs\_row

```python
def kwargs_row(obj: t.Callable[..., T] | type[T]) -> RowFactory[T]
```

RowFactory that uses the description to get the column names and builds a dictionary to be passed as kwargs.
the kwargs are then passed into the passed function or type/model

<a id="pinot_connect.rows.args_row"></a>

---
#### args\_row

```python
def args_row(obj: t.Callable[..., T] | type[T]) -> RowFactory[T]
```

Row factory that unpacks the row into positional arguments to the passed function or type/model

