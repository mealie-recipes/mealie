import json

import pytest


@pytest.fixture(scope="function")
def default_settings():
    return {
        "name": "main",
        "webhooks": {"webhookTime": "00:00", "webhookURLs": [], "enabled": False},
    }


@pytest.fixture(scope="session")
def default_theme(api_client):

    default_theme = {
        "name": "default",
        "colors": {
            "primary": "#E58325",
            "accent": "#00457A",
            "secondary": "#973542",
            "success": "#5AB1BB",
            "info": "#4990BA",
            "warning": "#FF4081",
            "error": "#EF5350",
        },
    }
    api_client.post("/api/site-settings/themes/create/", json=default_theme)

    return default_theme


@pytest.fixture(scope="session")
def new_theme():
    return {
        "name": "myTestTheme",
        "colors": {
            "primary": "#E58325",
            "accent": "#00457A",
            "secondary": "#973542",
            "success": "#5AB1BB",
            "info": "#4990BA",
            "warning": "#FF4081",
            "error": "#EF5350",
        },
    }


def test_default_settings(api_client, default_settings):
    response = api_client.get("/api/site-settings/")

    assert response.status_code == 200

    assert json.loads(response.content) == default_settings


def test_update_settings(api_client, default_settings):
    default_settings["webhooks"]["webhookURLs"] = [
        "https://test1.url.com",
        "https://test2.url.com",
        "https://test3.url.com",
    ]

    response = api_client.post("/api/site-settings/update/", json=default_settings)

    assert response.status_code == 200

    response = api_client.get("/api/site-settings/")
    assert json.loads(response.content) == default_settings


def test_default_theme(api_client, default_theme):
    response = api_client.get("/api/site-settings/themes/default/")
    assert response.status_code == 200
    assert json.loads(response.content) == default_theme


def test_create_theme(api_client, new_theme):

    response = api_client.post("/api/site-settings/themes/create/", json=new_theme)
    assert response.status_code == 200

    response = api_client.get(f"/api/site-settings/themes/{new_theme.get('name')}/")
    assert response.status_code == 200
    assert json.loads(response.content) == new_theme


def test_read_all_themes(api_client, default_theme, new_theme):
    response = api_client.get("/api/site-settings/themes/")
    assert response.status_code == 200
    assert json.loads(response.content) == [default_theme, new_theme]


def test_read_theme(api_client, default_theme, new_theme):
    for theme in [default_theme, new_theme]:
        response = api_client.get(f"/api/site-settings/themes/{theme.get('name')}/")
        assert response.status_code == 200
        assert json.loads(response.content) == theme


def test_delete_theme(api_client, default_theme, new_theme):
    for theme in [default_theme, new_theme]:
        response = api_client.delete(
            f"/api/site-settings/themes/{theme.get('name')}/delete/"
        )

        assert response.status_code == 200
