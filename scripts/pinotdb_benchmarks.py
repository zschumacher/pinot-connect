import asyncio
import gc
import statistics
import time
from abc import ABC
from abc import abstractmethod
from datetime import time

from pinotdb import db as pinotdb

import pinot_connect
from pinot_connect.rows import list_row


class Benchmark(ABC):
    name: str

    def __init_subclass__(cls, **kwargs):
        if not hasattr(cls, "name") and ABC not in cls.__bases__:
            raise ValueError(f"Missing 'name' attribute on {cls.__name__}")

    def __init__(self, iterations: int = 10, warmup: int = 0):
        self.iterations = iterations
        self.warmup = warmup

    @abstractmethod
    def pinot_connect_call(self, *args, **kwargs):
        ...

    def pinot_connect_warmup(self, *args, **kwargs):
        self.pinot_connect_call(*args, **kwargs)

    @abstractmethod
    def pinotdb_call(self, *args, **kwargs):
        self.pinotdb_call(*args, **kwargs)

    def pinotdb_warmup(self, *args, **kwargs):
        ...

    def measure_time(self, f, *args, **kwargs) -> list[float]:
        times = []
        for _ in range(self.iterations):
            start = time.perf_counter_ns()
            f(*args, **kwargs)
            times.append(time.perf_counter_ns() - start)
        return times

    def summarize(self, times: list[float]):
        return {
            "total": sum(times) / 1e6,
            "mean": statistics.mean(times) / 1e6,
            "median": statistics.median(times) / 1e6,
            "p95": statistics.quantiles(times, n=100)[94] / 1e6,
        }

    def print_results(self, pinot_connect_summary, pinot_db_summary):
        template = (
            "|             | {:>10} | {:>10} | {:>10} | {:>10} |\n"
            "| ----------- | ---------- | ---------- | ---------- | ---------- |\n"
            "| **pinot_connect** | {:>10.2f} | {:>10.2f} | {:>10.2f} | {:>10.2f} |\n"
            "| **pinotdb** | {:>10.2f} | {:>10.2f} | {:>10.2f} | {:>10.2f} |\n"
            "| **diff%**   | {:>9.2f}% | {:>9.2f}% | {:>9.2f}% | {:>9.2f}% |\n"
        ).format(
            "total",
            "avg",
            "median",
            "p95",
            pinot_connect_summary["total"],
            pinot_connect_summary["mean"],
            pinot_connect_summary["median"],
            pinot_connect_summary["p95"],
            pinot_db_summary["total"],
            pinot_db_summary["mean"],
            pinot_db_summary["median"],
            pinot_db_summary["p95"],
            100 * (pinot_connect_summary["total"] - pinot_db_summary["total"]) / pinot_connect_summary["total"],
            100 * (pinot_connect_summary["mean"] - pinot_db_summary["mean"]) / pinot_connect_summary["mean"],
            100 * (pinot_connect_summary["median"] - pinot_db_summary["median"]) / pinot_connect_summary["median"],
            100 * (pinot_connect_summary["p95"] - pinot_db_summary["p95"]) / pinot_connect_summary["p95"],
        )
        print(f"\n{self.name} Benchmark for {self.iterations} runs")
        print(template)

    def run(self, *args, **kwargs):
        gc.disable()
        try:
            for _ in range(self.warmup):
                self.pinot_connect_warmup(*args, **kwargs)
                self.pinotdb_warmup(*args, **kwargs)
            pinot_connect_time = self.measure_time(self.pinot_connect_call, *args, **kwargs)
            pinot_db_time = self.measure_time(self.pinotdb_call, *args, **kwargs)
        finally:
            gc.enable()

        pinot_connect_summary = self.summarize(pinot_connect_time)
        pinot_db_summary = self.summarize(pinot_db_time)

        self.print_results(pinot_connect_summary=pinot_connect_summary, pinot_db_summary=pinot_db_summary)


class AsyncBenchmark(Benchmark, ABC):
    @abstractmethod
    async def pinotdb_call(self, *args, **kwargs):
        ...

    async def pinotdb_warmup(self, *args, **kwargs):
        await self.pinotdb_call(*args, **kwargs)

    @abstractmethod
    async def pinot_connect_call(self, *args, **kwargs):
        ...

    async def pinot_connect_warmup(self, *args, **kwargs):
        await self.pinot_connect_call(*args, **kwargs)

    def summarize(self, times: list[float]):
        return {
            "total": sum(times) * 1000,
        }

    def print_results(self, pinot_connect_summary, pinot_db_summary):
        template = (
            "|             | {:>10} | \n"
            "| ----------- | ---------- |\n"
            "| **pinot_connect** | {:>10.2f} |\n"
            "| **pinotdb** | {:>10.2f} |\n"
            "| **diff%**   | {:>9.2f}% |\n"
        ).format(
            "total",
            pinot_connect_summary["total"],
            pinot_db_summary["total"],
            100 * (pinot_connect_summary["total"] - pinot_db_summary["total"]) / pinot_connect_summary["total"],
        )
        print(f"\n{self.name} Benchmark for {self.iterations} runs")
        print(template)

    async def measure_time(self, f, *args, **kwargs) -> list[float]:
        start = asyncio.get_running_loop().time()
        tasks = [asyncio.create_task(f(*args, **kwargs)) for _ in range(self.iterations)]
        await asyncio.gather(*tasks)
        end = asyncio.get_running_loop().time()
        return [end - start]

    async def run(self, *args, **kwargs):
        gc.disable()
        try:
            for _ in range(self.warmup):
                await self.pinot_connect_warmup(*args, **kwargs)
                await self.pinotdb_warmup(*args, **kwargs)
            pinot_connect_time = await self.measure_time(self.pinot_connect_call, *args, **kwargs)
            pinot_db_time = await self.measure_time(self.pinotdb_call, *args, **kwargs)
        finally:
            gc.enable()

        pinot_connect_summary = self.summarize(pinot_connect_time)
        pinot_db_summary = self.summarize(pinot_db_time)

        self.print_results(pinot_connect_summary=pinot_connect_summary, pinot_db_summary=pinot_db_summary)

    def run_with_asyncio(self, *args, **kwargs):
        asyncio.run(self.run(*args, **kwargs))


class BenchmarkFetch(Benchmark, ABC):
    def pinot_connect_call(self, pinot_connect_connection: pinot_connect.Connection, _, query: str):
        ...

    def pinotdb_call(self, _, pinotdb_connection: pinotdb.Connection, query: str):
        ...

    def run(self, query: str):
        pinot_connect_conn = pinot_connect.connect(host="localhost")
        pinotdb_conn = pinotdb.connect(host="localhost", path="/query", scheme="http")
        super().run(pinot_connect_conn, pinotdb_conn, query)


class AsyncFetchBenchmark(AsyncBenchmark, ABC):
    def pinot_connect_call(self, pinot_connect_connection: pinot_connect.Connection, _, query: str):
        ...

    def pinotdb_call(self, _, pinotdb_connection: pinotdb.Connection, query: str):
        ...

    async def run(self, query: str):
        pinot_connect_conn = await pinot_connect.AsyncConnection.connect(host="localhost")
        pinotdb_conn = pinotdb.connect_async(host="localhost", path="/query", scheme="http")
        await super().run(pinot_connect_conn, pinotdb_conn, query)

    def run_with_asyncio(self, query: str):
        asyncio.run(self.run(query))


class BenchmarkFetchone(BenchmarkFetch):
    name = "fetchone()"

    def pinot_connect_call(self, pinot_connect_connection: pinot_connect.Connection, _, query: str):
        cursor = pinot_connect_connection.cursor(row_factory=list_row)
        cursor.execute(query)
        cursor.fetchone()

    def pinotdb_call(self, _, pinotdb_connection: pinotdb.Connection, query: str):
        cursor = pinotdb_connection.cursor()
        cursor.execute(query)


class BenchmarkFetchoneAsync(AsyncFetchBenchmark):
    name = "async fetchone()"

    async def pinot_connect_call(self, pinot_connect_connection: pinot_connect.AsyncConnection, _, query: str):
        cursor = await pinot_connect_connection.cursor(row_factory=list_row)
        await cursor.execute(query)
        await cursor.fetchone()

    async def pinotdb_call(self, _, pinotdb_connection: pinotdb.AsyncConnection, query: str):
        cursor = pinotdb_connection.cursor()
        await cursor.execute(query)
        cursor.fetchone()


class BenchmarkFetchmany(BenchmarkFetch):
    name = "fetchmany(n)"

    def pinot_connect_call(self, pinot_connect_connection: pinot_connect.Connection, _, query: str):
        cursor = pinot_connect_connection.cursor(row_factory=list_row)
        cursor.execute(query)
        cursor.fetchmany(10)

    def pinotdb_call(self, _, pinotdb_connection: pinotdb.Connection, query: str):
        cursor = pinotdb_connection.cursor()
        cursor.execute(query)
        cursor.fetchmany(10)


class BenchmarkFetchmanyAsync(AsyncFetchBenchmark):
    name = "async fetchmany()"

    async def pinot_connect_call(self, pinot_connect_connection: pinot_connect.AsyncConnection, _, query: str):
        cursor = await pinot_connect_connection.cursor(row_factory=list_row)
        await cursor.execute(query)
        await cursor.fetchmany(10)

    async def pinotdb_call(self, _, pinotdb_connection: pinotdb.AsyncConnection, query: str):
        cursor = pinotdb_connection.cursor()
        await cursor.execute(query)
        cursor.fetchmany(10)


class BenchmarkFetchall(BenchmarkFetch):
    name = "fetchall()"

    def pinot_connect_call(self, pinot_connect_connection: pinot_connect.Connection, _, query: str):
        cursor = pinot_connect_connection.cursor(row_factory=list_row)
        cursor.execute(query)
        cursor.fetchall()

    def pinotdb_call(self, _, pinotdb_connection: pinotdb.Connection, query: str):
        cursor = pinotdb_connection.cursor()
        cursor.execute(query)
        cursor.fetchall()


class BenchmarkFetchallAsync(AsyncFetchBenchmark):
    name = "async fetchall()"

    async def pinot_connect_call(self, pinot_connect_connection: pinot_connect.AsyncConnection, _, query: str):
        cursor = await pinot_connect_connection.cursor(row_factory=list_row)
        await cursor.execute(query)
        await cursor.fetchall()

    async def pinotdb_call(self, _, pinotdb_connection: pinotdb.AsyncConnection, query: str):
        cursor = pinotdb_connection.cursor()
        await cursor.execute(query)
        cursor.fetchall()


if __name__ == "__main__":
    runs = 100
    query = "select * from githubComplexTypeEvents limit 1000"

    # for bm in BenchmarkFetchone, BenchmarkFetchmany, BenchmarkFetchall:
    #     bm(iterations=runs, warmup=1).run(query)

    for abm in BenchmarkFetchoneAsync, BenchmarkFetchmanyAsync, BenchmarkFetchallAsync:
        abm(iterations=runs, warmup=1).run_with_asyncio(query)
