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


def test_public_about_get_app_info_branding_defaults(api_client: TestClient, reset_branding_settings):
    branding = reset_branding_settings
    branding.name = "Mealie"
    branding.logo_path = None

    response = api_client.get(api_routes.app_about)
    as_dict = response.json()

    assert as_dict["brandingName"] == "Mealie"
    assert as_dict["brandingLogoUrl"] is None

    assert api_client.get(api_routes.app_about_branding_logo).status_code == 404


def test_public_about_get_app_info_branding_custom(api_client: TestClient, reset_branding_settings, tmp_path: Path):
    branding = reset_branding_settings

    logo_file = tmp_path / "logo.svg"
    logo_file.write_text("<svg></svg>")

    branding.name = "My Recipes"
    branding.logo_path = str(logo_file)

    response = api_client.get(api_routes.app_about)
    as_dict = response.json()

    assert as_dict["brandingName"] == "My Recipes"
    assert as_dict["brandingLogoUrl"] == "/api/app/about/branding-logo"

    logo_response = api_client.get(api_routes.app_about_branding_logo)
    assert logo_response.status_code == 200
    assert logo_response.content == b"<svg></svg>"


def test_public_about_get_app_info_branding_missing_file_falls_back(api_client: TestClient, reset_branding_settings):
    branding = reset_branding_settings
    branding.logo_path = "/nonexistent/path/logo.svg"

    response = api_client.get(api_routes.app_about)
    assert response.json()["brandingLogoUrl"] is None
    assert api_client.get(api_routes.app_about_branding_logo).status_code == 404
