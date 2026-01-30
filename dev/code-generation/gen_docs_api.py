import json
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI

from mealie.app import app
from mealie.core.config import determine_data_dir

DATA_DIR = determine_data_dir()

"""Script to export the ReDoc documentation page into a standalone HTML file."""

HTML_TEMPLATE = """<!-- Custom HTML site displayed as the Home chapter -->
{% extends "main.html" %}
{% block tabs %}
{{ super() }}

<style>
    body {
        margin: 0;
        padding: 0;
    }
</style>


<div id="redoc-container"></div>
<script src="https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js"> </script>
<script>
    var spec = MY_SPECIFIC_TEXT;
    Redoc.init(spec, {}, document.getElementById("redoc-container"));
</script>


{% endblock %}
{% block content %}{% endblock %}
{% block footer %}{% endblock %}
"""

HTML_PATH = DATA_DIR.parent.parent.joinpath("docs/docs/overrides/api.html")
CONSTANT_DT = datetime(2025, 10, 24, 15, 53, 0, 0, tzinfo=UTC)


def normalize_timestamps(s: dict[str, Any]) -> dict[str, Any]:
    field_format = s.get("format")
    is_timestamp = field_format in ["date-time", "date", "time"]
    has_default = s.get("default")

    if not is_timestamp:
        for k, v in s.items():
            if isinstance(v, dict):
                s[k] = normalize_timestamps(v)
            elif isinstance(v, list):
                s[k] = [normalize_timestamps(i) if isinstance(i, dict) else i for i in v]

        return s
    elif not has_default:
        return s

    if field_format == "date-time":
        s["default"] = CONSTANT_DT.isoformat()
    elif field_format == "date":
        s["default"] = CONSTANT_DT.date().isoformat()
    elif field_format == "time":
        s["default"] = CONSTANT_DT.time().isoformat()

    return s


def generate_api_docs(my_app: FastAPI):
    openapi_schema = my_app.openapi()
    openapi_schema = normalize_timestamps(openapi_schema)

    with open(HTML_PATH, "w") as fd:
        text = HTML_TEMPLATE.replace("MY_SPECIFIC_TEXT", json.dumps(openapi_schema))
        fd.write(text)


if __name__ == "__main__":
    generate_api_docs(app)
