# pinot-connect

[![codecov](https://codecov.io/gh/zschumacher/pinot-connect/graph/badge.svg?token=bQLhy9S1GT)](https://codecov.io/gh/zschumacher/pinot-connect)
[![unit-tests](https://github.com/zschumacher/pinot-connect/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/zschumacher/pinot-connect/actions/workflows/unit-tests.yml)
[![integration-tests](https://github.com/zschumacher/pinot-connect/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/zschumacher/pinot-connect/actions/workflows/integration-tests.yml)
[![pages-build-deployment](https://github.com/zschumacher/pinot-connect/actions/workflows/pages/pages-build-deployment/badge.svg)](https://github.com/zschumacher/pinot-connect/actions/workflows/pages/pages-build-deployment)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Installation
```shell
pip install pinot-connect
# or
poetry add pinot-connect
# or
uv add pinot-connect
```

## Overview
**pinot_connect** is a **DB-API 2.0 compliant** and **statically typed** driver for querying **Apache Pinot** with 
Python. It supports both **synchronous** and **asynchronous** execution, making it flexible for a variety of 
applications.

Powered by:

- [**orjson**](https://github.com/ijl/orjson) for **high-performance JSON deserialization**
- [**httpx**](https://www.python-httpx.org) for **async support and connection pooling**

`pinot_connect` outperforms `pinotdb` in benchmarks.  On average for queries that return 100 or more rows, you can 
expect to see ~15-30% faster execution. 

---
## Documentation
The full documentation can be found [here](https://www.pinot-connect.org).

---
## Quickstart

### Running a quick start Pinot cluster
To start an Apache Pinot cluster with example data, run:
```shell
docker run -d --name pinot-quickstart -p 9000:9000 \
  -p 8099:8000 \
  --health-cmd="curl -f http://localhost:9000/health || exit 1" \
  --health-interval=10s \
  --health-timeout=5s \
  --health-retries=5 \
  --health-start-period=10s \
  apachepinot/pinot:latest QuickStart -type batch
```
This command launches a Pinot instance with preloaded batch data, making it easy to start querying right away.

### Querying with `pinot_connect`
Once your cluster is up and running, you can query it using pinot_connect. Below are examples for both synchronous and 
asynchronous usage.

``` py title="Sync example"
import pinot_connect
from pinot_connect.rows import dict_row

with pinot_connect.connect(host="localhost") as conn:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute("select * from airlineStats limit 100")
        for row in cursor:
            print(row)
```

``` py title="Async example"
import pinot_connect
from pinot_connect.rows import dict_row
import asyncio

async def main():
    async with pinot_connect.AsyncConnection.connect(hose="localhost") as conn:
        async with conn.cursor(row_factory=dict_row) as cursor:
            await cursor.execute("select * from airlineStats limit 100")
            async for row in cursor:
                print(row)

asyncio.run(main())
```

**What's Happening Here?**

- **Standard DB-API 2.0 Interface**  
  `pinot_connect` provides a familiar connection and cursor interface, similar to popular Python database clients such as
  `sqlite3` or `psycopg`

- **Row Factories**  
  The `row_factory` parameter lets you customize how rows are returned. In this example, `dict_row` returns results as
  dictionaries. You can choose from built-in factories or define your own. See the 
  [**row factories documentation**](https://www.pinot-connect.org/usage/row_factories/) for details.

- **Type Mapping**  
  `pinot_connect` automatically converts Pinot data types to their Python equivalents. More details are available in the 
  [**type conversion documentation**](https://www.pinot-connect.org/usage/basic/#converting-types).

- **Cursor Iteration & Fetch Methods**  
  You can iterate over results directly or use `fetchone()`, `fetchmany()`, `fetchall()`, and `scroll()`, following the 
  DB-API spec. See the [**usage docs**](https://www.pinot-connect.org/usage/) or [**reference docs**](https://www.pinot-connect.org/reference/) for more details.

