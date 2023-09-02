from fastapi.testclient import TestClient
from src.main import app
from src.mapper.validator import Validator


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello by Santi!"}


def test_read_status():
    response = client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}


def test_patch_payload_validation_success(mocker):
    # Create a mock instance of Validator for simulating a success
    mock_validator_class = mocker.patch("src.main.Validator")
    mock_validator_instance = mock_validator_class.return_value
    mock_validator_instance.validate_payload.return_value = True

    # Create a mock instance of Mapper
    mock_mapper_class = mocker.patch("src.main.Mapper")
    mock_mapper_instance = mock_mapper_class.return_value
    mock_mapper_instance.convert_payload.return_value = {"key_after_mapper": "value"}

    payload = {"key_before_mapper": "value"}
    response = client.patch("/quotes", json=payload)

    assert response.status_code == 200
    assert response.json() == {"key_after_mapper": "value"}

    # Assert that the Validator and Mapper classes were called once
    mock_validator_class.assert_called_once()
    mock_validator_instance.validate_payload.assert_called_once_with(payload)
    mock_mapper_class.assert_called_once_with(payload)
    mock_mapper_instance.convert_payload.assert_called_once()


def test_patch_payload_validation_failure(mocker):
    # Create a mock instance of Validator for simulating a failure
    mock_validator_class = mocker.patch("src.main.Validator")
    mock_validator_instance = mock_validator_class.return_value
    mock_validator_instance.validate_payload.return_value = {
        "Error": "Payload schema validation error",
    }

    # Create a mock instance of Mapper
    mock_mapper_class = mocker.patch("src.main.Mapper")

    payload = {"key_before_mapper": "value"}
    response = client.patch("/quotes", json=payload)

    assert response.status_code == 400
    assert "Error" in response.json()["detail"]

    # Assert that the Validator and Mapper classes were called once
    mock_validator_class.assert_called_once()
    mock_validator_instance.validate_payload.assert_called_once_with(payload)
    mock_mapper_class.assert_not_called()
