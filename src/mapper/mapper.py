import os
import json
import re
import pprint
from typing import Dict, Optional

from jsonpath_ng.ext import parse

from .validator import Validator


class Mapper:
    """
    Mapper implementation that enables Read/Write operations from on a JSON
    Mapper document with JMESPath Standards for "sources" and "destinations" of
    2 different JSON files (considered as the "input" and "output" definitions).
    """

    def __init__(
        self,
        payload: Dict[str, object],
        json_mapper: Optional[Dict[str, object]] = None,
    ) -> None:
        self.payload = payload
        self.json_mapper = json_mapper
        if self.json_mapper is None:
            self._load_json_mapper()

    def _load_json_mapper(self) -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(current_dir, "models")
        json_mapper_path = os.path.join(models_dir, "mapper.json")

        with open(json_mapper_path, "r") as json_mapper_file:
            self.json_mapper = json.load(json_mapper_file)

    def convert_payload(self) -> dict:
        final_payload = {"quotes": []}
        for element in self.json_mapper["mapper"]:
            print(f"\nProcessing mapper element: {element}")

            # Read source
            source_jsonpath = parse(element["source"])
            matched_result = source_jsonpath.find(self.payload)

            print(len(matched_result))

            for match in matched_result:
                pprint.pprint(f"value: {match.value}")
                pprint.pprint(f"match.full_path: {str(match.full_path)}")

                # Write destination
                pprint.pprint("---- beginning destination part ----")
                indexes = self.extract_indexes(str(match.full_path))
                pprint.pprint(f"indexes: {indexes}")

                pprint.pprint(f"element['destination']: {element['destination']}")
                # pprint.pprint(f"final_payload: {final_payload}")

                updated_element_destination = self.inject_indexes(
                    element["destination"], indexes
                )

                destination_jsonpath = parse(updated_element_destination)
                pprint.pprint(f"destination_jsonpath: {destination_jsonpath}")
                destination_jsonpath.update_or_create(final_payload, match.value)
                pprint.pprint(final_payload)
                pprint.pprint("---- end destination part ----")
            # return

        return final_payload

    def extract_indexes(self, path):
        """
        Returns a list of the required indexes based on the groups that are part
        of an input string with inner elements that follow this:
        --> Begins with "["
        --> Ends with "]"

        Examples:
            1. "hello.value" returns []
            2. "hello.list1[0].value.list2[3].othervalue" returns [0, 3]
            3. "hello.list1[2].value" returns [2]
        """

        pattern = r"\[(\d+)\]"
        indexes = re.findall(pattern, path)
        return [int(index) for index in indexes]

    def inject_indexes(self, path, indexes):
        """
        Returns a string with inner elements that follow follow this pattern
        replaced to the corresponding indexes replaced:
        --> Begins with "["
        --> Ends with "]"
        The input string must follow the JMESPath standards.

        Examples:
            1. ("value", []) returns "value"
            2. ("list1[*].value.list2[*].result", [1, 2]) returns "list1[1].value.list2[2].result"
            3. ("list1[*].value", [*]) returns "list1[2].value"
        """
        for index in indexes:
            path = re.sub(r"\[\*\]", f"[{index}]", path, count=1)
        return path
