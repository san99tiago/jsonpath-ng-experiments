import os
import json
import pytest
from jsonschema import ValidationError
from src.mapper.validator import Validator


# Mocking jsonschema.validate to control validation results
@pytest.fixture
def mock_jsonschema_validate(mocker):
    return mocker.patch("jsonschema.validate")


def test_validator_init_without_schema(mocker):
    # Mocking "open" and "join" to avoid OS files usage
    mock_os_path_join = mocker.patch("os.path.join", return_value="fake_schema_path")
    mock_open = mocker.patch(
        "src.mapper.validator.open", mocker.mock_open(read_data='{"type": "object"}')
    )

    validator = Validator()

    assert mock_os_path_join.call_count == 2
    mock_open.assert_called_once_with("fake_schema_path", "r")
    assert validator.schema == {"type": "object"}


def test_validator_init_with_schema(mocker):
    mock_os_path_join = mocker.patch("os.path.join")
    schema = {"type": "object"}

    validator = Validator(schema)

    mock_os_path_join.assert_not_called()
    assert validator.schema == schema


def test_validator_good_payload_success():
    from src.mapper.validator import Validator

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "source_payload_good_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    validator = Validator()
    assert validator.validate_payload(payload) is True


def test_validator_bad_payload_failure():
    from src.mapper.validator import Validator

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "source_payload_bad_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    validator = Validator()
    result = validator.validate_payload(payload)

    assert result["Error"] == "Payload schema validation error"
