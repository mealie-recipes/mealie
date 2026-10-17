from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


@pytest.fixture(autouse=True)
def _reset_app_theme(unfiltered_database: AllRepositories) -> Generator[None]:
    # app_theme is an instance-wide singleton, so a leftover row would bleed into
    # unrelated tests (including the public /app/about/theme ones) if left behind.
    yield
    unfiltered_database.app_theme.delete_all()


def test_admin_theme_get_defaults_to_env_settings(api_client: TestClient, admin_user: TestUser):
    settings = get_app_settings()

    response = api_client.get(api_routes.admin_theme, headers=admin_user.token)
    assert response.status_code == 200

    as_dict = response.json()
    assert as_dict["lightPrimary"] == settings.theme.light_primary
    assert as_dict["darkPrimary"] == settings.theme.dark_primary


def test_admin_theme_update_persists_and_is_served_publicly(api_client: TestClient, admin_user: TestUser):
    payload = {
        "lightPrimary": "#123456",
        "lightAccent": "#234567",
        "lightSecondary": "#345678",
        "lightSuccess": "#456789",
        "lightInfo": "#56789A",
        "lightWarning": "#6789AB",
        "lightError": "#789ABC",
        "darkPrimary": "#ABCDEF",
        "darkAccent": "#BCDEF0",
        "darkSecondary": "#CDEF01",
        "darkSuccess": "#DEF012",
        "darkInfo": "#EF0123",
        "darkWarning": "#F01234",
        "darkError": "#012345",
    }

    response = api_client.put(api_routes.admin_theme, json=payload, headers=admin_user.token)
    assert response.status_code == 200
    for key, value in payload.items():
        assert response.json()[key] == value

    # a second GET returns the same saved override, not the env defaults
    response = api_client.get(api_routes.admin_theme, headers=admin_user.token)
    assert response.json()["lightPrimary"] == "#123456"

    # the public, unauthenticated endpoint the frontend actually loads on boot
    # must reflect the override too
    response = api_client.get(api_routes.app_about_theme)
    assert response.status_code == 200
    assert response.json()["lightPrimary"] == "#123456"
    assert response.json()["darkPrimary"] == "#ABCDEF"


def test_admin_theme_update_twice_overwrites_the_same_row(
    api_client: TestClient, admin_user: TestUser, unfiltered_database: AllRepositories
):
    first_payload = {"lightPrimary": "#111111"}
    second_payload = {"lightPrimary": "#222222"}

    base = api_client.get(api_routes.admin_theme, headers=admin_user.token).json()
    base.update(first_payload)
    api_client.put(api_routes.admin_theme, json=base, headers=admin_user.token)

    base.update(second_payload)
    api_client.put(api_routes.admin_theme, json=base, headers=admin_user.token)

    rows = unfiltered_database.app_theme.get_all()
    assert len(rows) == 1
    assert rows[0].light_primary == "#222222"


def test_admin_theme_reset_removes_the_override(
    api_client: TestClient, admin_user: TestUser, unfiltered_database: AllRepositories
):
    settings = get_app_settings()

    base = api_client.get(api_routes.admin_theme, headers=admin_user.token).json()
    base["lightPrimary"] = "#ABCABC"
    api_client.put(api_routes.admin_theme, json=base, headers=admin_user.token)
    assert len(unfiltered_database.app_theme.get_all()) == 1

    response = api_client.delete(api_routes.admin_theme, headers=admin_user.token)
    assert response.status_code == 204
    assert len(unfiltered_database.app_theme.get_all()) == 0

    response = api_client.get(api_routes.app_about_theme)
    assert response.json()["lightPrimary"] == settings.theme.light_primary


def test_admin_theme_requires_admin(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(api_routes.admin_theme, headers=unique_user.token)
    assert response.status_code == 403

    response = api_client.put(api_routes.admin_theme, json={}, headers=unique_user.token)
    assert response.status_code == 403
