import pytest

from pinot_connect.rows import _get_column_names
from pinot_connect.rows import args_row
from pinot_connect.rows import dict_row
from pinot_connect.rows import dict_row_load_json_fields
from pinot_connect.rows import kwargs_row
from pinot_connect.rows import list_row
from pinot_connect.rows import tuple_row


class MockColumn:
    def __init__(self, name: str):
        self.name = name


@pytest.fixture
def column_description():
    return [MockColumn("col1"), MockColumn("col2"), MockColumn("col3")]


@pytest.fixture
def row_values():
    return ["val1", "val2", '{"foo": "bar"}']


def test_get_column_names(column_description):
    assert _get_column_names(column_description) == ["col1", "col2", "col3"]


def test_tuple_row(column_description, row_values):
    row_maker = tuple_row(column_description)
    assert row_maker(row_values) == tuple(row_values)


def test_list_row(column_description, row_values):
    row_maker = list_row(column_description)
    assert row_maker(row_values) == row_values


def test_dict_row(column_description, row_values):
    row_maker = dict_row(column_description)
    expected_dict = {"col1": "val1", "col2": "val2", "col3": '{"foo": "bar"}'}
    assert row_maker(row_values) == expected_dict


@pytest.fixture
def sample_dataclass():
    from dataclasses import dataclass

    @dataclass
    class Sample:
        col1: str
        col2: str
        col3: str

    return Sample


def test_kwargs_row(column_description, row_values, sample_dataclass):
    row_factory = kwargs_row(sample_dataclass)
    row_maker = row_factory(column_description)
    obj = row_maker(row_values)

    assert isinstance(obj, sample_dataclass)
    assert obj.col1 == "val1"
    assert obj.col2 == "val2"
    assert obj.col3 == '{"foo": "bar"}'


def test_args_row_function(column_description, row_values):
    def sample_function(col1, col2, col3):
        return f"{col1}-{col2}-{col3}"

    row_factory = args_row(sample_function)
    row_maker = row_factory(column_description)

    assert row_maker(row_values) == 'val1-val2-{"foo": "bar"}'


def test_args_row_class(column_description, row_values):
    class Sample:
        def __init__(self, col1, col2, col3):
            self.col1 = col1
            self.col2 = col2
            self.col3 = col3

    row_factory = args_row(Sample)
    row_maker = row_factory(column_description)
    obj = row_maker(row_values)

    assert isinstance(obj, Sample)
    assert obj.col1 == "val1"
    assert obj.col2 == "val2"
    assert obj.col3 == '{"foo": "bar"}'


def test_dict_row_load_json_fields(column_description, row_values):
    row_factory = dict_row_load_json_fields("col3")
    row_maker = row_factory(column_description)
    obj = row_maker(row_values)
    print(obj)
    assert obj["col1"] == "val1"
    assert obj["col2"] == "val2"
    assert obj["col3"] == {"foo": "bar"}
