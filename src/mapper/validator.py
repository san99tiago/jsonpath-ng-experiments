import os
import json
from typing import Dict, Optional, Union, Literal, Any
import jsonschema


class Validator:
    """
    JSON Validator implementation based on a schema and a payload.
    """

    def __init__(self, schema: Optional[Dict[str, object]] = None) -> None:
        self.schema = schema
        if self.schema is None:
            self._load_schema()

    def _load_schema(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "models")
        schema_path = os.path.join(models_dir, "source_schema.json")

        with open(schema_path, "r") as schema_file:
            self.schema = json.load(schema_file)

    def validate_payload(
        self,
        payload: Dict[str, object],
    ) -> Union[Literal[True], dict]:
        try:
            jsonschema.validate(
                instance=payload,
                schema=self.schema,
            )
            return True
        except jsonschema.ValidationError as val_error:
            print(
                f"Validation error with payload. Error message: {val_error.message}, json_path: {val_error.json_path}"
            )
            return {
                "Error": "Payload schema validation error",
                "Details": {
                    "Message": val_error.message,
                    "JsonPath": val_error.json_path,
                },
            }
