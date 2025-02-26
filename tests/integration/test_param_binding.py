import datetime

import orjson
import pytest

ACTOR = {
    "id": 18542751,
    "login": "LimeVista",
    "display_login": "LimeVista",
    "gravatar_id": "",
    "url": "https://api.github.com/users/LimeVista",
    "avatar_url": "https://avatars.githubusercontent.com/u/18542751?",
}


@pytest.mark.vcr
class TestSync:
    @pytest.mark.parametrize(
        "query, params",
        [
            ("select AirTime from airlineStats where AirTime > %s limit 10", (200,)),
            ("select AirTime from airlineStats where AirTime > %(air_time)s limit 10", {"air_time": 200}),
        ],
    )
    def test_int_binding(self, cursor, query, params):
        response = cursor.execute(query, params)
        assert response.status_code == 200
        rows = cursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] > 200 for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            ("select lat from starbucksStores where lat > %s limit 10", (61.2,)),
            ("select lat from starbucksStores where lat > %(latitude)s limit 10", {"latitude": 61.2}),
        ],
    )
    def test_float_binding(self, cursor, query, params):
        response = cursor.execute(query, params)
        assert response.status_code == 200
        rows = cursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] > 61.2 for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            (
                "select created_at_timestamp from githubEvents where created_at_timestamp > %s limit 10",
                (datetime.datetime(2018, 1, 1, 11, 2),),
            ),
            (
                "select created_at_timestamp from githubEvents where created_at_timestamp > %(ts)s limit 10",
                {"ts": datetime.datetime(2018, 1, 1, 11, 2)},
            ),
        ],
    )
    def test_datetime_binding(self, cursor, query, params):
        response = cursor.execute(query, params)
        assert response.status_code == 200
        rows = cursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] > datetime.datetime(2018, 1, 1, 11, 2) for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            ("select type from githubEvents where type = %s limit 10", ("PushEvent",)),
            ("select type from githubEvents where type = %(event_type)s limit 10", {"event_type": "PushEvent"}),
        ],
    )
    def test_str_binding(self, cursor, query, params):
        response = cursor.execute(query, params)
        assert response.status_code == 200
        rows = cursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] == "PushEvent" for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            # test tuples
            ("select teamName from dimBaseballTeams where teamID in %s", (("ANA", "ARI", "ATL"),)),
            ("select teamName from dimBaseballTeams where teamID in %(teams)s", {"teams": ("ANA", "ARI", "ATL")}),
            # test lists
            ("select teamName from dimBaseballTeams where teamID in %s", (["ANA", "ARI", "ATL"],)),
            ("select teamName from dimBaseballTeams where teamID in %(teams)s", {"teams": ["ANA", "ARI", "ATL"]}),
            # test sets
            ("select teamName from dimBaseballTeams where teamID in %s", ({"ANA", "ARI", "ATL"},)),
            ("select teamName from dimBaseballTeams where teamID in %(teams)s", {"teams": {"ANA", "ARI", "ATL"}}),
        ],
    )
    def test_sequence_binding(self, cursor, query, params):
        response = cursor.execute(query, params)
        assert response.status_code == 200
        rows = cursor.fetchall()
        assert [i[0] for i in rows] == ["Anaheim Angels", "Arizona Diamondbacks", "Atlanta Braves"]

    @pytest.mark.parametrize(
        "query, params",
        [
            ("select actor from githubEvents where actor = %s", (ACTOR,)),
            ("select actor from githubEvents where actor = %(actor)s", {"actor": ACTOR}),
        ],
    )
    def test_dict_binding(self, cursor, query, params):
        response = cursor.execute(query, params)
        assert response.status_code == 200
        rows = cursor.fetchall()
        assert len(rows) == 2
        assert all(orjson.loads(i[0]) == ACTOR for i in rows)


@pytest.mark.vcr
@pytest.mark.asyncio
class TestAsync:
    @pytest.mark.parametrize(
        "query, params",
        [
            ("select AirTime from airlineStats where AirTime > %s limit 10", (200,)),
            ("select AirTime from airlineStats where AirTime > %(air_time)s limit 10", {"air_time": 200}),
        ],
    )
    async def test_int_binding(self, acursor, query, params):
        response = await acursor.execute(query, params)
        assert response.status_code == 200
        rows = await acursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] > 200 for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            ("select lat from starbucksStores where lat > %s limit 10", (61.2,)),
            ("select lat from starbucksStores where lat > %(latitude)s limit 10", {"latitude": 61.2}),
        ],
    )
    async def test_float_binding(self, acursor, query, params):
        response = await acursor.execute(query, params)
        assert response.status_code == 200
        rows = await acursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] > 61.2 for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            (
                "select created_at_timestamp from githubEvents where created_at_timestamp > %s limit 10",
                (datetime.datetime(2018, 1, 1, 11, 2),),
            ),
            (
                "select created_at_timestamp from githubEvents where created_at_timestamp > %(ts)s limit 10",
                {"ts": datetime.datetime(2018, 1, 1, 11, 2)},
            ),
        ],
    )
    async def test_datetime_binding(self, acursor, query, params):
        response = await acursor.execute(query, params)
        assert response.status_code == 200
        rows = await acursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] > datetime.datetime(2018, 1, 1, 11, 2) for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            ("select type from githubEvents where type = %s limit 10", ("PushEvent",)),
            ("select type from githubEvents where type = %(event_type)s limit 10", {"event_type": "PushEvent"}),
        ],
    )
    async def test_str_binding(self, acursor, query, params):
        response = await acursor.execute(query, params)
        assert response.status_code == 200
        rows = await acursor.fetchall()
        assert len(rows) == 10
        assert all(i[0] == "PushEvent" for i in rows)

    @pytest.mark.parametrize(
        "query, params",
        [
            # test tuples
            ("select teamName from dimBaseballTeams where teamID in %s", (("ANA", "ARI", "ATL"),)),
            ("select teamName from dimBaseballTeams where teamID in %(teams)s", {"teams": ("ANA", "ARI", "ATL")}),
            # test lists
            ("select teamName from dimBaseballTeams where teamID in %s", (["ANA", "ARI", "ATL"],)),
            ("select teamName from dimBaseballTeams where teamID in %(teams)s", {"teams": ["ANA", "ARI", "ATL"]}),
            # test sets
            ("select teamName from dimBaseballTeams where teamID in %s", ({"ANA", "ARI", "ATL"},)),
            ("select teamName from dimBaseballTeams where teamID in %(teams)s", {"teams": {"ANA", "ARI", "ATL"}}),
        ],
    )
    async def test_sequence_binding(self, acursor, query, params):
        response = await acursor.execute(query, params)
        assert response.status_code == 200
        rows = await acursor.fetchall()
        assert [i[0] for i in rows] == ["Anaheim Angels", "Arizona Diamondbacks", "Atlanta Braves"]

    @pytest.mark.parametrize(
        "query, params",
        [
            ("select actor from githubEvents where actor = %s", (ACTOR,)),
            ("select actor from githubEvents where actor = %(actor)s", {"actor": ACTOR}),
        ],
    )
    async def test_dict_binding(self, acursor, query, params):
        response = await acursor.execute(query, params)
        assert response.status_code == 200
        rows = await acursor.fetchall()
        assert len(rows) == 2
        assert all(orjson.loads(i[0]) == ACTOR for i in rows)
