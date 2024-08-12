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

    # Smoke Test - Test the endpoint returns something that's a the expected shape
    assert as_dict["emailReady"] in [True, False]
    assert as_dict["ldapReady"] in [True, False]
    assert as_dict["baseUrlSet"] in [True, False]
    assert as_dict["isUpToDate"] in [True, False]
