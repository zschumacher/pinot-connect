import pytest
import pytest_asyncio

from pinot_connect import AsyncConnection
from pinot_connect import AsyncCursor
from pinot_connect import Cursor
from pinot_connect import connect
from pinot_connect.exceptions import ProgrammingError


class TestSync:
    @pytest.fixture(autouse=True)
    def execute_query(self, cursor, ten_starbucks_stores):
        cursor.execute("select * from starbucksStores limit 10")
        assert cursor.description
        assert cursor.rowcount == 10
        return cursor

    def test_fetchone(self, cursor: Cursor):
        assert cursor.rownumber == 0
        row = cursor.fetchone()
        assert isinstance(row, tuple)
        assert len(row) == len(cursor.description)
        assert cursor.rownumber == 1

    def test_fetchmany(self, cursor: Cursor):
        # default arraysize
        assert cursor.rownumber == 0
        rows = cursor.fetchmany()
        assert len(rows) == 1
        assert isinstance(rows[0], tuple)
        assert cursor.rownumber == 1

        # set arraysize
        cursor.arraysize = 5
        rows = cursor.fetchmany()
        assert len(rows) == 5
        assert all(isinstance(row, tuple) for row in rows)
        assert cursor.rownumber == 6

        # pass value
        rows = cursor.fetchmany(3)
        assert len(rows) == 3
        assert all(isinstance(row, tuple) for row in rows)
        assert cursor.rownumber == 9

        # exhaust cursor
        rows = cursor.fetchmany(100)
        assert len(rows) == 1
        rows = cursor.fetchmany(100)
        assert rows == []

    def test_fetchall(self, cursor: Cursor):
        assert cursor.rownumber == 0
        rows = cursor.fetchall()
        assert cursor.rownumber == 10
        assert len(rows) == 10
        assert all(isinstance(row, tuple) for row in rows)

    def test_scroll_relative_errors(self, cursor: Cursor):
        with pytest.raises(ProgrammingError):
            cursor.scroll(-1)

        with pytest.raises(ProgrammingError):
            cursor.scroll(0)

        with pytest.raises(IndexError):
            cursor.scroll(11)

    def test_scroll_relative(self, cursor: Cursor):
        assert cursor.rownumber == 0
        cursor.scroll(1)
        assert cursor.rownumber == 1
        cursor.scroll(9)
        assert cursor.rownumber == 10

    def test_scroll_absolute_errors(self, cursor: Cursor):
        with pytest.raises(ProgrammingError):
            cursor.scroll(-1, mode="absolute")

        cursor.scroll(1)
        with pytest.raises(ProgrammingError):
            cursor.scroll(0)

        with pytest.raises(ProgrammingError):
            cursor.scroll(1, mode="absolute")

        with pytest.raises(IndexError):
            cursor.scroll(11, mode="absolute")

    def test_scroll_absolute(self, cursor: Cursor):
        assert cursor.rownumber == 0
        cursor.scroll(3, mode="absolute")
        assert cursor.rownumber == 3
        cursor.scroll(4, mode="absolute")
        assert cursor.rownumber == 4
        cursor.scroll(10, mode="absolute")
        assert cursor.rownumber == 10

    def test_iteration(self, cursor: Cursor):
        assert cursor.rownumber == 0
        rows = [r for r in cursor]
        assert len(rows) == 10


@pytest.mark.asyncio
class TestAsync:
    @pytest_asyncio.fixture
    async def acursor(self, ten_starbucks_stores, acursor):
        await acursor.execute("select * from starbucksStores limit 10")
        assert acursor.description
        assert acursor.rowcount == 10
        return acursor

    async def test_fetchone(self, acursor: AsyncCursor):
        assert acursor.rownumber == 0
        row = await acursor.fetchone()
        assert isinstance(row, tuple)
        assert len(row) == len(acursor.description)
        assert acursor.rownumber == 1

    async def test_fetchmany(self, acursor: AsyncCursor):
        # default arraysize
        assert acursor.rownumber == 0
        rows = await acursor.fetchmany()
        assert len(rows) == 1
        assert isinstance(rows[0], tuple)
        assert acursor.rownumber == 1

        # set arraysize
        acursor.arraysize = 5
        rows = await acursor.fetchmany()
        assert len(rows) == 5
        assert all(isinstance(row, tuple) for row in rows)
        assert acursor.rownumber == 6

        # pass value
        rows = await acursor.fetchmany(3)
        assert len(rows) == 3
        assert all(isinstance(row, tuple) for row in rows)
        assert acursor.rownumber == 9

        # exhaust cursor
        rows = await acursor.fetchmany(100)
        assert len(rows) == 1
        rows = await acursor.fetchmany(100)
        assert rows == []

    async def test_fetchall(self, acursor: AsyncCursor):
        assert acursor.rownumber == 0
        rows = await acursor.fetchall()
        assert acursor.rownumber == 10
        assert len(rows) == 10
        assert all(isinstance(row, tuple) for row in rows)

    async def test_scroll_relative_errors(self, acursor: AsyncCursor):
        with pytest.raises(ProgrammingError):
            await acursor.scroll(-1)

        with pytest.raises(ProgrammingError):
            await acursor.scroll(0)

        with pytest.raises(IndexError):
            await acursor.scroll(11)

    async def test_scroll_relative(self, acursor: AsyncCursor):
        assert acursor.rownumber == 0
        await acursor.scroll(1)
        assert acursor.rownumber == 1
        await acursor.scroll(9)
        assert acursor.rownumber == 10

    async def test_scroll_absolute_errors(self, acursor: AsyncCursor):
        with pytest.raises(ProgrammingError):
            await acursor.scroll(-1, mode="absolute")

        await acursor.scroll(1)
        with pytest.raises(ProgrammingError):
            await acursor.scroll(0)

        with pytest.raises(ProgrammingError):
            await acursor.scroll(1, mode="absolute")

        with pytest.raises(IndexError):
            await acursor.scroll(11, mode="absolute")

    async def test_scroll_absolute(self, acursor: AsyncCursor):
        assert acursor.rownumber == 0
        await acursor.scroll(3, mode="absolute")
        assert acursor.rownumber == 3
        await acursor.scroll(4, mode="absolute")
        assert acursor.rownumber == 4
        await acursor.scroll(10, mode="absolute")
        assert acursor.rownumber == 10

    async def test_iteration(self, acursor: AsyncCursor):
        rows = [r async for r in acursor]
        assert len(rows) == 10
