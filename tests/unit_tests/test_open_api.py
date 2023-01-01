from openapi_spec_validator import openapi_v30_spec_validator, validate_spec

from mealie.app import app


def test_validate_open_api_spec():
    open_api = app.openapi()
    validate_spec(open_api, validator=openapi_v30_spec_validator)
