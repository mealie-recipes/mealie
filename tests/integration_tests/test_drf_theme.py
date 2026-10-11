import os

import django
from django.test import Client


def setup_django():
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "mealie.drf_api.settings",
    )
    django.setup()


def test_drf_theme_matches_fastapi(api_client):
    setup_django()
    path = "/api/app/about/theme"

    legacy = api_client.get(path)
    migrated = Client().get(path)

    assert migrated.status_code == legacy.status_code == 200
    assert migrated.json() == legacy.json()
    assert migrated.headers["Content-Type"] == legacy.headers["Content-Type"]
    assert migrated.headers["Cache-Control"] == legacy.headers["Cache-Control"] == "public, max-age=604800"


def test_drf_theme_trailing_slash_matches_fastapi(api_client):
    setup_django()
    path = "/api/app/about/theme/"

    legacy = api_client.get(path, follow_redirects=False)
    migrated = Client().get(path, follow=False)

    assert migrated.status_code == legacy.status_code == 307
    assert migrated.headers["Location"] == legacy.headers["Location"]


def test_drf_theme_post_matches_fastapi(api_client):
    setup_django()
    path = "/api/app/about/theme"

    legacy = api_client.post(path, json={})
    migrated = Client().post(
        path,
        data="{}",
        content_type="application/json",
    )

    assert migrated.status_code == legacy.status_code == 405
    assert migrated.json() == legacy.json()
    assert migrated.headers["Allow"] == legacy.headers["Allow"]
