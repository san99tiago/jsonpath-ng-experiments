import os
import json
from typing import Dict, Optional
from jsonschema import validate, ValidationError


class Validator:
    """
    JSON Validator implementation based on a schema and a payload.
    """

    def __init__(
        self, payload: Dict[str, object], schema: Optional[Dict[str, object]] = None
    ) -> None:
        self.payload = payload
        self.schema = schema
        if self.schema is None:
            self._load_schema()
        self._validate_payload()

    def _load_schema(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "models")
        schema_path = os.path.join(models_dir, "schema.json")

        with open(schema_path, "r") as schema_file:
            self.schema = json.load(schema_file)

    def _validate_payload(self) -> None:
        try:
            validate(
                instance=self.payload,
                schema=self.schema,
            )
        except ValidationError as e:
            raise ValueError("Payload validation error: " + str(e))
