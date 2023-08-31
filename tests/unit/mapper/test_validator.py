import os
import json
import pytest


def test_validator_success():
    from src.mapper.validator import Validator

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "source_payload_good_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    validator = Validator()
    assert validator.validate_payload(payload) is True


def test_validator_failure():
    from src.mapper.validator import Validator

    current_dir = os.path.dirname(os.path.abspath(__file__))
    payload_path = os.path.join(current_dir, "source_payload_bad_01.json")

    with open(payload_path, "r") as payload_file:
        payload = json.load(payload_file)

    validator = Validator()
    result = validator.validate_payload(payload)

    assert result["Error"] == "Payload schema validation error"
