"""Migration contract captured from the original application before replacement."""

import json
from pathlib import Path

from mealie.app import app

ORIGINAL = json.loads((Path(__file__).parents[1] / "data/http/original-openapi.json").read_text())


def test_original_paths_methods_and_parameter_contracts():
    current = app.openapi()
    assert current["paths"].keys() == ORIGINAL["paths"].keys()
    for path, operations in ORIGINAL["paths"].items():
        assert current["paths"][path].keys() == operations.keys(), path
        for method, operation in operations.items():
            migrated = current["paths"][path][method]

            def parameters(value):
                return {(item["name"], item["in"], item.get("required", False)) for item in value.get("parameters", [])}

            assert parameters(migrated) == parameters(operation), (path, method)
            assert migrated["responses"].keys() == operation["responses"].keys(), (path, method)
            assert ("requestBody" in migrated) == ("requestBody" in operation), (path, method)


def normalize_schema(value):
    if isinstance(value, dict):
        return {key: normalize_schema(item) for key, item in value.items() if key not in ("title", "description")}
    if isinstance(value, list):
        return [normalize_schema(item) for item in value]
    return value


def test_original_schema_components_and_security_contracts():
    current = app.openapi()
    assert normalize_schema(current["components"]) == normalize_schema(ORIGINAL["components"])
    for path, operations in ORIGINAL["paths"].items():
        for method, operation in operations.items():
            assert current["paths"][path][method].get("security") == operation.get("security"), (path, method)
