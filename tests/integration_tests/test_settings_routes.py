import json

import pytest
from fastapi.testclient import TestClient

from mealie.schema.admin import SiteSettings
from tests.app_routes import AppRoutes


@pytest.fixture(scope="function")
def default_settings():
    return SiteSettings().dict(by_alias=True)


def test_default_settings(api_client: TestClient, api_routes: AppRoutes, default_settings):
    response = api_client.get(api_routes.site_settings)

    assert response.status_code == 200

    assert json.loads(response.content) == default_settings


def test_update_settings(api_client: TestClient, api_routes: AppRoutes, default_settings, admin_token):
    default_settings["language"] = "fr"
    default_settings["showRecent"] = False

    response = api_client.put(api_routes.site_settings, json=default_settings, headers=admin_token)

    assert response.status_code == 200

    response = api_client.get(api_routes.site_settings)
    assert json.loads(response.content) == default_settings
