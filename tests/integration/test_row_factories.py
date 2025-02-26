import dataclasses

import pytest

from pinot_connect import rows


@dataclasses.dataclass
class StarbucksStore:
    lon: float
    lat: float
    name: str
    address: str
    location_st_point: str


class TestSync:
    @pytest.mark.parametrize(
        "row_factory, expected_type",
        [
            (rows.dict_row, dict),
            (rows.tuple_row, tuple),
            (rows.list_row, list),
            (rows.kwargs_row(StarbucksStore), StarbucksStore),
            (rows.args_row(StarbucksStore), StarbucksStore),
        ],
    )
    def test_list_row(self, connection, ten_starbucks_stores, row_factory, expected_type):
        cursor = connection.cursor(row_factory=row_factory)
        cursor.execute("select * from starbucksStores limit 10")
        assert all(isinstance(r, expected_type) for r in cursor.fetchall())

    @pytest.mark.vcr
    def test_dict_row_load_json_fields(self, connection):
        cursor = connection.cursor(row_factory=rows.dict_row_load_json_fields("actor", "repo", "payload"))
        cursor.execute("select actor, repo, payload from githubEvents limit 10")

        rows_ = cursor.fetchall()
        assert len(rows_) == 10
        for row in rows_:
            assert isinstance(row["actor"], dict)
            assert isinstance(row["repo"], dict)
            assert isinstance(row["payload"], dict)


@pytest.mark.asyncio
class TestAsync:
    @pytest.mark.parametrize(
        "row_factory, expected_type",
        [
            (rows.dict_row, dict),
            (rows.tuple_row, tuple),
            (rows.list_row, list),
            (rows.kwargs_row(StarbucksStore), StarbucksStore),
            (rows.args_row(StarbucksStore), StarbucksStore),
        ],
    )
    async def test_list_row(self, aconnection, ten_starbucks_stores, row_factory, expected_type):
        cursor = await aconnection.cursor(row_factory=row_factory)
        await cursor.execute("select * from starbucksStores limit 10")
        rows_ = await cursor.fetchall()
        assert len(rows_) == 10
        assert all(isinstance(r, expected_type) for r in rows_)

    @pytest.mark.vcr
    async def test_dict_row_load_json_fields(self, aconnection):
        cursor = await aconnection.cursor(row_factory=rows.dict_row_load_json_fields("actor", "repo", "payload"))
        await cursor.execute("select actor, repo, payload from githubEvents limit 10")

        rows_ = await cursor.fetchall()
        assert len(rows_) == 10
        for row in rows_:
            assert isinstance(row["actor"], dict)
            assert isinstance(row["repo"], dict)
            assert isinstance(row["payload"], dict)
