import os
import json
import pytest


def test_validator_success():
    from src.mapper.validator import Validator

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "payload_good_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    Validator(payload)


def test_validator_failure():
    from src.mapper.validator import Validator

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "payload_bad_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    with pytest.raises(Exception) as e:
        Validator(payload)

    assert "Payload validation error" in str(e.value)
