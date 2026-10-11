import os

import django
import pytest
from django.test import Client

from mealie.core.config import get_app_settings
from mealie.db.db_setup import session_context
from mealie.repos.all_repositories import get_repositories


def setup_django() -> None:
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE",
        "mealie.drf_api.settings",
    )
    django.setup()


@pytest.mark.parametrize(
    "path",
    [
        "/api/app/about",
        "/api/app/about/startup-info",
    ],
)
def test_drf_about_matches_fastapi(api_client, path):
    setup_django()

    legacy = api_client.get(path)
    migrated = Client().get(path)

    assert migrated.status_code == legacy.status_code == 200
    assert migrated.json() == legacy.json()
    assert migrated.headers["Content-Type"] == legacy.headers["Content-Type"]


@pytest.mark.parametrize("private_group", [True, False])
@pytest.mark.parametrize("private_household", [True, False])
def test_drf_about_privacy(
    api_client,
    unfiltered_database,
    private_group,
    private_household,
):
    setup_django()

    settings = get_app_settings()
    group = unfiltered_database.groups.get_by_name(settings.DEFAULT_GROUP)
    assert group and group.preferences

    with session_context() as session:
        group_repos = get_repositories(
            session,
            group_id=group.id,
            household_id=None,
        )
        household = group_repos.households.get_by_name(settings.DEFAULT_HOUSEHOLD)
        assert household and household.preferences
        assert household.group_id == group.id

    original_group_privacy = group.preferences.private_group
    original_household_privacy = household.preferences.private_household

    try:
        group.preferences.private_group = private_group
        unfiltered_database.group_preferences.update(
            group.id,
            group.preferences,
        )

        household.preferences.private_household = private_household
        unfiltered_database.household_preferences.update(
            household.id,
            household.preferences,
        )

        legacy = api_client.get("/api/app/about")
        migrated = Client().get("/api/app/about")

        assert migrated.status_code == legacy.status_code == 200
        assert migrated.json() == legacy.json()

        payload = migrated.json()
        assert payload["defaultGroupSlug"] == (None if private_group else group.slug)
        assert payload["defaultHouseholdSlug"] == (None if private_group or private_household else household.slug)
    finally:
        group.preferences.private_group = original_group_privacy
        unfiltered_database.group_preferences.update(
            group.id,
            group.preferences,
        )

        household.preferences.private_household = original_household_privacy
        unfiltered_database.household_preferences.update(
            household.id,
            household.preferences,
        )


@pytest.mark.parametrize(
    "path",
    [
        "/api/app/about/",
        "/api/app/about/startup-info/",
    ],
)
def test_drf_about_redirect_matches_fastapi(api_client, path):
    setup_django()

    url = f"{path}?example=value"
    legacy = api_client.get(url, follow_redirects=False)
    migrated = Client().get(url, follow=False)

    assert migrated.status_code == legacy.status_code == 307
    assert migrated.headers["Location"] == legacy.headers["Location"]


@pytest.mark.parametrize(
    "path",
    [
        "/api/app/about",
        "/api/app/about/startup-info",
    ],
)
def test_drf_about_post_matches_fastapi(api_client, path):
    setup_django()

    legacy = api_client.post(path, json={})
    migrated = Client().post(
        path,
        data="{}",
        content_type="application/json",
    )

    assert migrated.status_code == legacy.status_code == 405
    assert migrated.json() == legacy.json()
    assert migrated.headers["Allow"] == legacy.headers["Allow"]
