from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from mealie.core.settings.static import APP_VERSION
from mealie.repos.repository_factory import AllRepositories
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False], ids=["private group", "public group"])
def test_public_about_get_app_info(
    api_client: TestClient, is_private_group: bool, unfiltered_database: AllRepositories
):
    settings = get_app_settings()
    group = unfiltered_database.groups.get_by_name(settings.DEFAULT_GROUP)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    unfiltered_database.group_preferences.update(group.id, group.preferences)

    response = api_client.get(api_routes.app_about)
    as_dict = response.json()

    assert as_dict["production"] == settings.PRODUCTION
    assert as_dict["version"] == APP_VERSION
    assert as_dict["demoStatus"] == settings.IS_DEMO
    assert as_dict["allowSignup"] == settings.ALLOW_SIGNUP

    if is_private_group:
        assert as_dict["defaultGroupSlug"] is None
    else:
        assert as_dict["defaultGroupSlug"] == group.slug


def test_admin_about_get_app_info(api_client: TestClient, admin_user: TestUser):
    response = api_client.get(api_routes.admin_about, headers=admin_user.token)

    as_dict = response.json()

    settings = get_app_settings()

    assert as_dict["version"] == APP_VERSION
    assert as_dict["demoStatus"] == settings.IS_DEMO
    assert as_dict["apiPort"] == settings.API_PORT
    assert as_dict["apiDocs"] == settings.API_DOCS
    assert as_dict["dbType"] == settings.DB_ENGINE
    # assert as_dict["dbUrl"] == settings.DB_URL_PUBLIC
    assert as_dict["defaultGroup"] == settings.DEFAULT_GROUP


def test_admin_about_get_app_statistics(api_client: TestClient, admin_user: TestUser):
    response = api_client.get(api_routes.admin_about_statistics, headers=admin_user.token)

    as_dict = response.json()

    # Smoke Test - Test the endpoint returns something that's a number
    assert as_dict["totalRecipes"] >= 0
    assert as_dict["uncategorizedRecipes"] >= 0
    assert as_dict["untaggedRecipes"] >= 0
    assert as_dict["totalUsers"] >= 0
    assert as_dict["totalGroups"] >= 0


def test_admin_about_check_app_config(api_client: TestClient, admin_user: TestUser):
    response = api_client.get(api_routes.admin_about_check, headers=admin_user.token)

    as_dict = response.json()

    settings = get_app_settings()

    # Smoke Test - Test the endpoint returns something that's a the expected shape
    assert as_dict["emailReady"] in [True, False]
    assert as_dict["ldapReady"] in [True, False]
    assert as_dict["oidcReady"] in [True, False]
    assert as_dict["baseUrlSet"] in [True, False]
    assert as_dict["isUpToDate"] in [True, False]

    # The disabled flags report whether the auth provider is turned off entirely,
    # which is independent of whether its remaining settings are fully configured
    assert as_dict["ldapDisabled"] == (not settings.LDAP_AUTH_ENABLED)
    assert as_dict["oidcDisabled"] == (not settings.OIDC_AUTH_ENABLED)


@pytest.fixture
def reset_branding_settings():
    branding = get_app_settings().branding
    original = branding.model_dump()
    yield branding
    for key, value in original.items():
        setattr(branding, key, value)


def test_public_about_get_app_branding_defaults(api_client: TestClient, reset_branding_settings):
    branding = reset_branding_settings
    branding.name = "Mealie"
    branding.html_title = "Mealie"
    branding.icon_path = None
    branding.favicon_path = None

    response = api_client.get(api_routes.app_about_branding)
    as_dict = response.json()

    assert as_dict["name"] == "Mealie"
    assert as_dict["htmlTitle"] == "Mealie"
    assert as_dict["iconUrl"] is None
    assert as_dict["faviconUrl"] is None

    assert api_client.get(api_routes.app_about_branding_icon).status_code == 404
    assert api_client.get(api_routes.app_about_branding_favicon).status_code == 404


def test_public_about_get_app_branding_custom(api_client: TestClient, reset_branding_settings, tmp_path: Path):
    branding = reset_branding_settings

    icon_file = tmp_path / "icon.svg"
    icon_file.write_text("<svg></svg>")
    favicon_file = tmp_path / "favicon.ico"
    favicon_file.write_bytes(b"fake-favicon")

    branding.name = "My Recipes"
    branding.html_title = "My Recipes - Home"
    branding.icon_path = str(icon_file)
    branding.favicon_path = str(favicon_file)

    response = api_client.get(api_routes.app_about_branding)
    as_dict = response.json()

    assert as_dict["name"] == "My Recipes"
    assert as_dict["htmlTitle"] == "My Recipes - Home"
    assert as_dict["iconUrl"] == "/api/app/about/branding/icon"
    assert as_dict["faviconUrl"] == "/api/app/about/branding/favicon"

    icon_response = api_client.get(api_routes.app_about_branding_icon)
    assert icon_response.status_code == 200
    assert icon_response.content == b"<svg></svg>"

    favicon_response = api_client.get(api_routes.app_about_branding_favicon)
    assert favicon_response.status_code == 200
    assert favicon_response.content == b"fake-favicon"


def test_public_about_get_app_branding_missing_file_falls_back(api_client: TestClient, reset_branding_settings):
    branding = reset_branding_settings
    branding.icon_path = "/nonexistent/path/icon.svg"

    response = api_client.get(api_routes.app_about_branding)
    assert response.json()["iconUrl"] is None
    assert api_client.get(api_routes.app_about_branding_icon).status_code == 404
