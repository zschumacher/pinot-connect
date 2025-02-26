# Row Factories

## Introduction

Row factories are a feature in `pinot_connect` that allow users to customize the format of query results. By default, query 
results are returned as tuples.  They are heavily inspired by a feature with the same name in *psycopg*.   *pinot_connect* 
ships with a handful of userful row factories, but it is also easy to define your own.  Row factories are typed with 
generics and typevars to ensure static type checkers (such as mypy) will correctly check the return types.

!!! Warning 
    Because Apache Pinot's query protocol is http/https and the data is returned via json, data is serialized from the
    server as a list of lists.  Using a `list_row` factory gives the best performance, because it does not modify the 
    data.  The default, though, is `tuple_row` to maintain DB-API compliance.  The performance penalty is small, but it 
    can add up on large result sets.

---

## How Row Factories Work

Internally, row factories work by processing each row of the query result set and transforming it into the desired 
format before being returned to the user. This transformation is achieved through user-defined functions or callable 
objects that serve as the "factory" for producing rows.  These transformations are done lazily and guarantees each row
is only ever processed exactly once.  
Some common use cases include:

* Returning rows as dictionaries
* Returning rows as a user defined object, such as a dataclass or *pydantic* model
* Passing the row as kwargs or args to a function 
* Loading json strings returned from pinot into python objects (since pinot always returns them as strings over the api)

This functionality ensures that users have full control over the structure and format of their query results.

---
## Examples
### Built in row factories

All examples assume the below code has been ran first

``` py
import dataclasses
from typing import Self

import pinot_connect
from pinot_connect import rows

connection = pinot_connect.connect(host="localhost")
```

!!! note ""

    === "tuple_row | list_row | dict_row"
        ``` py title="tuple_row"
        with conn.cursor() as cursor:  # do not have to pass, tuple_row is default
            cursor.execute("select * from airlineStats limit 10")
            print(type(cursor.fetchone())  # tuple
        ```

        ``` py title="dict_row"
        with conn.cursor(row_factory=rows.dict_row) as cursor:
            cursor.execute("select * from airlineStats limit 10")
            print(type(cursor.fetchone())  # dict
        ```

        ``` py title="list_row"
        with conn.cursor(row_factory=rows.list_row) as cursor:
            cursor.execute("select * from airlineStats limit 10)
            print(type(cursor.fetchone()) # list
        ```

    === "kwargs_row"
        ``` py title="Using an object"
        @dataclass.dataclass
        class AirTime:
            AirTime: int
            AirlineID: int

        with conn.cursor(row_factory=rows.kwargs_row(AirTime)) as cursor:
            cursor.execute("select AirTime, AirLineID from airlineStats limit 10")
            print(type(cursor.fetchone))  # AirTime
        ```

        ``` py title="Using a function"
        @dataclass.dataclass
        class AirTime:
            air_time: int
            air_line_id: int

            @classmethod
            def from_row(cls, **row) -> Self:
                return cls(air_time=row['AirTime'], air_line_id=row['AirlineID'])

        with conn.cursor(row_factory=rows.kwargs_row(AirTime.from_row)):
            cursor.execute("select AirTime, AirLineID from airlineStats limit 10")
            print(type(cursor.fetchone)) # AirTime
        ```
    === "args_row"
        ``` py title="Using an object"
        class AirTime:
            def __init__(air_time: int, air_line_id: int):
                self.air_time = air_time
                self.air_line_id = air_line_id
            
        # rows.kwargs_row -> RowFactory[AirTime]
        with conn.cursor(row_factory=rows.args_row(AirTime)) as cursor:
            cursor.execute("select * from airlineStats limit 10")
            print(type(cursor.fetchone))  # AirTime
        ```

        ``` py title="Using a function"
        def print_and_return(*args) -> tuple:
            print(args)
            return args

        with conn.cursor(row_factory=rows.args_row(print_and_return)):
            cursor.execute("select * from airlineStats limit 10")
            print(type(cursor.fetchone)) # tuple
        ```

    === "dict_row_load_json_fields"
        !!! info
            Over the API Pinot returns JSON columns as strings, and also indicates the column type as a string.  Often
            time, you will want to serialize the json columns to python objects.  This row factory handles doing that
            efficiently and returning the fields as values in a dict row; in other row factories, the value will always
            be a string.
        ```py
        with conn.cursor(row_factory=rows.dict_row_load_json_fields("actor", "payload"):
            cursor.execute("select actor, payload, id from githubEvents limit 10")
            row = cursor.fetchone()
            print(type(row['actor']))  # dict
            print(type(row['payload'])) # dict
        ```

---

### Writing your own row factories
It is simple to write your own row factories - when doing so, it is important to use the types defined in `pinot_connect.rows`
to ensure correct static typing.

- `RowType` when the type is determined by something passed to an outer function, such as `pinot_connect.rows.kwargs_row`.  
  When doing this, you should also make sure the outer function returns `RowFactory[RowType]`
- `RowMaker` should be returned from every `RowFactory` function.

Let's look at how you might write your own factory that always validates a row with *pydantic*.  This example assume that
you have *pydantic* already installed.

```py
import pydantic
from pinot_connect.rows import RowMaker
from pinot_connect import Column
from typing import Iterator

class AirlineStats(pydantic.BaseModel):
    air_time: int = pydantic.Field(..., alias="AirTime")
    air_line_id: int = pydantic.Field(..., alias="AirlineID")

def airline_stats_row(description: list[Column]) -> RowMaker[AirlineStats]:
    # important to do this at top level of the function so we only have to build column names once per query
    column_names = [i[0] for i in description]
    
    def airline_stats_row_(values: Iterator) -> AirlineStats:
        data = dict(zip(column_names, values))
        return AirlineStats(**data)
    
    return airline_stats_row_
    
with connection.cursor(row_factory=airline_stats_row) as cursor:
    cursor.execute("select * from airlineStats limit 10")
    print(type(cursor.fetchone()))  # AirlineStats
```


