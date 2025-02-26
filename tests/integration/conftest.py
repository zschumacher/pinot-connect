import pathlib

import pytest
import pytest_asyncio
import vcr

from pinot_connect import AsyncConnection
from pinot_connect import connect


@pytest.fixture
def cassette_dir():
    return pathlib.Path(__file__).parent / "cassettes"


@pytest.fixture
def ten_starbucks_stores(cassette_dir):
    with vcr.use_cassette(f"{cassette_dir}/starbucksStores-Limit10.yaml"):
        yield


@pytest.fixture
def connection():
    with connect("localhost") as conn:
        yield conn


@pytest.fixture
def cursor(connection):
    with connection.cursor() as c:
        yield c


@pytest_asyncio.fixture
async def aconnection():
    async with AsyncConnection.connect("localhost") as conn:
        yield conn


@pytest_asyncio.fixture
async def acursor(aconnection):
    async with aconnection.cursor() as c:
        yield c
