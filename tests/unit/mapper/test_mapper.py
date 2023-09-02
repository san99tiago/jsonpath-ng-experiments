import os
import json
import pytest
from src.mapper.mapper import Mapper


# Mocking os.path.join to avoid reading a real JSON mapper file
@pytest.fixture
def mock_os_path_join(mocker):
    return mocker.patch("os.path.join", return_value="fake_mapper_path")


def test_mapper_init_without_json_mapper(mock_os_path_join, mocker):
    mock_os_path_join.return_value = "fake_mapper_path"
    mock_open = mocker.patch(
        "src.mapper.mapper.open", mocker.mock_open(read_data='{"mapper": "[]"}')
    )

    mapper = Mapper({})

    assert mock_os_path_join.call_count == 2
    mock_open.assert_called_once_with("fake_mapper_path", "r")
    assert "mapper" in mapper.json_mapper
    assert mapper.payload == {}


def test_mapper_init_with_json_mapper(mock_os_path_join):
    json_mapper = {"mapper": []}
    mapper = Mapper({}, json_mapper=json_mapper)
    mock_os_path_join.assert_not_called()
    assert mapper.json_mapper == json_mapper
    assert mapper.payload == {}


def test_mapper_extract_indexes():
    mapper = Mapper({})
    assert mapper.extract_indexes("hello.value") == []
    assert mapper.extract_indexes("hello.list1[0].value.list2[3].othervalue") == [0, 3]
    assert mapper.extract_indexes("hello.list1[2].value") == [2]


def test_mapper_inject_indexes():
    mapper = Mapper({})
    assert mapper.inject_indexes("value", []) == "value"
    assert (
        mapper.inject_indexes("list1[*].value.list2[*].result", [1, 2])
        == "list1[1].value.list2[2].result"
    )
    assert mapper.inject_indexes("list1[*].value", [2]) == "list1[2].value"


def test_mapper_apply_transform_logic_with_default():
    mapper = Mapper({})
    logic = {
        "CASE": {
            "enumsMapping": [{"inputValue": "input", "outputValue": "output"}],
            "default": "defaultValue",
        }
    }

    match_value_in_case = "input"
    transformed_value = mapper.apply_transform_logic(match_value_in_case, logic)
    assert transformed_value == "output"

    match_value_not_in_case = "unknown"
    transformed_value = mapper.apply_transform_logic(match_value_not_in_case, logic)
    assert transformed_value == "defaultValue"


def test_mapper_apply_transform_logic_without_default():
    mapper = Mapper({})
    logic = {
        "CASE": {
            "enumsMapping": [{"inputValue": "input", "outputValue": "output"}],
        }
    }

    match_value_not_in_case = "other"
    transformed_value = mapper.apply_transform_logic(match_value_not_in_case, logic)
    assert transformed_value == "other"


def test_mapper_convert_payload_direct():
    payload = {
        "key1": "value1",
        "key2": "value2",
        "key3": {"inner_key": "inner_value"},
    }

    json_mapper = {
        "mapper": [
            {"source": "$.key1", "destination": "new_key1"},
            {"source": "$.key2", "destination": "super.cool.new_key2"},
            {"source": "$.key3.inner_key", "destination": "another.cool.new_key3"},
            {"source": "$.key4", "destination": "new_key4"},
        ]
    }

    mapper = Mapper(payload, json_mapper)
    transformed_payload = mapper.convert_payload()

    assert transformed_payload == {
        "another": {"cool": {"new_key3": "inner_value"}},
        "new_key1": "value1",
        "super": {"cool": {"new_key2": "value2"}},
    }


def test_mapper_convert_payload_multiple():
    payload = {
        "myList": [
            {
                "key1": "value1A",
                "key2": "value2A",
                "key3": "value3A",
            },
            {
                "key1": "value1B",
                "key2": "value2B",
                "key3": "value3B",
            },
            {
                "key1": "value1C",
                "key2": "value2C",
                "key3": "value3C",
                "key4": "value4C",
            },
        ],
    }

    json_mapper = {
        "mapper": [
            {"source": "$.myList[*].key1", "destination": "hi.newList[*].id1"},
            {
                "source": "$.myList[*].key2",
                "destination": "hi.newList[*].id2",
                "logic": {
                    "CASE": {
                        "enumsMapping": [
                            {
                                "inputValue": "value2B",
                                "outputValue": "SUPER_TRANSFORMED_VALUE_2B",
                            }
                        ],
                    }
                },
            },
            {"source": "$.myList[*].key3", "destination": "hi.newList[*].id3"},
            {"source": "$.myList[*].key4", "destination": "hi.newList[*].id4"},
        ]
    }

    mapper = Mapper(payload, json_mapper)
    transformed_payload = mapper.convert_payload()

    assert transformed_payload == {
        "hi": {
            "newList": [
                {"id1": "value1A", "id2": "value2A", "id3": "value3A"},
                {
                    "id1": "value1B",
                    "id2": "SUPER_TRANSFORMED_VALUE_2B",
                    "id3": "value3B",
                },
                {
                    "id1": "value1C",
                    "id2": "value2C",
                    "id3": "value3C",
                    "id4": "value4C",
                },
            ]
        }
    }


def test_mapper_real_complete_payload_01():
    from src.mapper.mapper import Mapper

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "source_payload_good_01.json")
    response_path = os.path.join(current_dir, "destination_response_good_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    with open(response_path, "r") as response_file:
        expected_response = json.load(response_file)

    mapper = Mapper(payload)
    assert mapper.convert_payload() == expected_response
