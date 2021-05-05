import json

import pytest
from fastapi.testclient import TestClient
from mealie.schema.settings import SiteSettings
from mealie.schema.theme import SiteTheme
from tests.app_routes import AppRoutes


@pytest.fixture(scope="function")
def default_settings():
    return SiteSettings().dict(by_alias=True)


@pytest.fixture(scope="session")
def default_theme():
    return SiteTheme(id=1).dict()


@pytest.fixture(scope="session")
def new_theme():
    return {
        "id": 3,
        "name": "myTestTheme",
        "colors": {
            "primary": "#E58325",
            "accent": "#00457A",
            "secondary": "#973542",
            "success": "#43A047",
            "info": "#4990BA",
            "warning": "#FF4081",
            "error": "#EF5350",
        },
    }


def test_default_settings(api_client: TestClient, api_routes: AppRoutes, default_settings):
    response = api_client.get(api_routes.site_settings)

    assert response.status_code == 200

    assert json.loads(response.content) == default_settings


def test_update_settings(api_client: TestClient, api_routes: AppRoutes, default_settings, token):
    default_settings["language"] = "fr"
    default_settings["showRecent"] = False

    response = api_client.put(api_routes.site_settings, json=default_settings, headers=token)

    assert response.status_code == 200

    response = api_client.get(api_routes.site_settings)
    assert json.loads(response.content) == default_settings


def test_default_theme(api_client: TestClient, api_routes: AppRoutes, default_theme):
    response = api_client.get(api_routes.themes_theme_name(1))
    assert response.status_code == 200
    assert json.loads(response.content) == default_theme


def test_create_theme(api_client: TestClient, api_routes: AppRoutes, new_theme, token):

    response = api_client.post(api_routes.themes_create, json=new_theme, headers=token)
    assert response.status_code == 201

    response = api_client.get(api_routes.themes_theme_name(new_theme.get("id")), headers=token)
    assert response.status_code == 200
    assert json.loads(response.content) == new_theme


def test_read_all_themes(api_client: TestClient, api_routes: AppRoutes, default_theme, new_theme):
    response = api_client.get(api_routes.themes)
    assert response.status_code == 200
    response_dict = json.loads(response.content)
    assert default_theme in response_dict
    assert new_theme in response_dict


def test_read_theme(api_client: TestClient, api_routes: AppRoutes, default_theme, new_theme):
    for theme in [default_theme, new_theme]:
        response = api_client.get(api_routes.themes_theme_name(theme.get("id")))
        assert response.status_code == 200
        assert json.loads(response.content) == theme


def test_update_theme(api_client: TestClient, api_routes: AppRoutes, token, default_theme, new_theme):
    theme_colors = {
        "primary": "#E12345",
        "accent": "#012345",
        "secondary": "#973542",
        "success": "#5AB1BB",
        "info": "#4990BA",
        "warning": "#FF4081",
        "error": "#EF4432",
    }

    new_theme["colors"] = theme_colors
    response = api_client.put(api_routes.themes_theme_name(new_theme.get("id")), json=new_theme, headers=token)
    assert response.status_code == 200
    response = api_client.get(api_routes.themes_theme_name(new_theme.get("id")))
    assert json.loads(response.content) == new_theme


def test_delete_theme(api_client: TestClient, api_routes: AppRoutes, default_theme, new_theme, token):
    for theme in [default_theme, new_theme]:
        response = api_client.delete(api_routes.themes_theme_name(theme.get("id")), headers=token)

        assert response.status_code == 200
