import os
import json
import re
import pprint
from typing import Dict, Optional

from jsonpath_ng.ext import parse


class Mapper:
    """
    A Mapper implementation facilitating Read/Write operations on a JSON Mapper
    document using JMESPath standards for "sources" and "destinations" of two
    different JSON files (referred to as "input" and "output" definitions).
    """

    def __init__(
        self,
        payload: Dict[str, object],
        json_mapper: Optional[Dict[str, object]] = None,
    ) -> None:
        """
        Initialize the Mapper with the provided payload and JSON mapper.

        Args:
            payload (Dict[str, object]): The input JSON payload.
            json_mapper (Optional[Dict[str, object]]): The JSON mapper definition.
                If not provided, it will be loaded from the default path.
        """
        self.payload = payload
        self.json_mapper = json_mapper
        if self.json_mapper is None:
            self._load_json_mapper()

    def _load_json_mapper(self) -> None:
        """
        Load the JSON mapper definition from the default path.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "models")
        json_mapper_path = os.path.join(models_dir, "mapper.json")

        with open(json_mapper_path, "r") as json_mapper_file:
            self.json_mapper = json.load(json_mapper_file)

    def convert_payload(self) -> dict:
        """
        Convert the payload using the JSON mapper logic.

        Returns:
            dict: The transformed payload.
        """
        transformed_payload = {}
        for element in self.json_mapper["mapper"]:
            print("\n----- Processing mapper element -----")
            print(f"--> element: {element}")
            batch_updates = []
            source_jsonpath = parse(element["source"])
            destination_path = element["destination"]
            matched_result = source_jsonpath.find(self.payload)

            for match in matched_result:
                match_value = match.value
                match_full_path = str(match.full_path)
                pprint.pprint(f"match_value: {match_value}")
                pprint.pprint(f"match_full_path: {match_full_path}")

                if "logic" in element:
                    match_value = self.apply_transform_logic(
                        match_value, element["logic"]
                    )
                    pprint.pprint(f"match_value (transformed): {match_value}")

                # Convert the destination path compatible to "write" operations
                indexes_from_match = self.extract_indexes(match_full_path)
                # pprint.pprint(f"indexes_from_match: {indexes_from_match}")

                updated_destination_path = self.inject_indexes(
                    destination_path, indexes_from_match
                )
                pprint.pprint(f"updated_destination_path: {updated_destination_path}")

                batch_updates.append((updated_destination_path, match_value))

            # Batch update transformed_payload for all found elements
            print("\n\n----- Creating the transformed payload for element -----")
            print(f"--> element: {element}")
            for updated_path, value in batch_updates:
                # pprint.pprint(f"updated_path: {updated_path}")
                # pprint.pprint(f"value: {value}")
                destination_jsonpath = parse(updated_path)
                destination_jsonpath.update_or_create(transformed_payload, value)
            pprint.pprint(f"transformed_payload: {transformed_payload}")

        return transformed_payload

    def extract_indexes(self, path):
        """
        Extract the required indexes from an input string containing
        inner elements following the format:
        --> Starts with "["
        --> Ends with "]"

        Examples:
            1. "hello.value" returns []
            2. "hello.list1[0].value.list2[3].othervalue" returns [0, 3]
            3. "hello.list1[2].value" returns [2]

        Args:
            path (str): The input string.

        Returns:
            list: A list of extracted indexes.
        """
        pattern = r"\[(\d+)\]"
        indexes = re.findall(pattern, path)
        return [int(index) for index in indexes]

    def inject_indexes(self, path, indexes):
        """
        Inject the given indexes into the input string where placeholders
        follow the format:
        --> Starts with "["
        --> Ends with "]"
        The input string must adhere to JMESPath standards.

        Examples:
            1. ("value", []) returns "value"
            2. ("list1[*].value.list2[*].result", [1, 2]) returns "list1[1].value.list2[2].result"
            3. ("list1[*].value", [*]) returns "list1[2].value"

        Args:
            path (str): The input string.
            indexes (list): The list of indexes to inject.

        Returns:
            str: The updated string with injected indexes.
        """
        for index in indexes:
            path = re.sub(r"\[\*\]", f"[{index}]", path, count=1)
        return path

    def apply_transform_logic(self, match_value, logic):
        """
        Apply the transformation logic to the source value based on the provided logic.

        Args:
            match_value: The source value to be transformed.
            logic: The transformation logic.

        Returns:
            The transformed value.
        """
        if "CASE" in logic and "enumsMapping" in logic["CASE"]:
            enums_mapping = logic["CASE"]["enumsMapping"]
            for enum in enums_mapping:
                if match_value == enum["inputValue"]:
                    return enum["outputValue"]
            if "default" in logic["CASE"]:
                return logic["CASE"]["default"]
        return match_value
