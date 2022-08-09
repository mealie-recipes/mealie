from openapi_spec_validator import validate_v3_spec

from mealie.app import app


def test_validate_open_api_spec():
    open_api = app.openapi()
    validate_v3_spec(open_api)
