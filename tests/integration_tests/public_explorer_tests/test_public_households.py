from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from mealie.schema.household.household import HouseholdCreate
from mealie.schema.household.household_preferences import CreateHouseholdPreferences
from mealie.services.household_services.household_service import HouseholdService
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False])
def test_get_all_households(api_client: TestClient, unique_user: TestUser, is_private_group: bool):
    unique_user.repos.group_preferences.patch(UUID(unique_user.group_id), {"private_group": is_private_group})
    households = [
        HouseholdService.create_household(
            unique_user.repos,
            HouseholdCreate(name=random_string()),
            CreateHouseholdPreferences(private_household=False),
        )
        for _ in range(5)
    ]

    response = api_client.get(api_routes.explore_groups_group_slug_households(unique_user.group_id))
    if is_private_group:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        response_ids = [item["id"] for item in response.json()["items"]]
        for household in households:
            assert str(household.id) in response_ids


@pytest.mark.parametrize("is_private_group", [True, False])
def test_get_all_households_public_only(api_client: TestClient, unique_user: TestUser, is_private_group: bool):
    unique_user.repos.group_preferences.patch(UUID(unique_user.group_id), {"private_group": is_private_group})
    public_household = HouseholdService.create_household(
        unique_user.repos,
        HouseholdCreate(name=random_string()),
        CreateHouseholdPreferences(private_household=False),
    )
    private_household = HouseholdService.create_household(
        unique_user.repos,
        HouseholdCreate(name=random_string()),
        CreateHouseholdPreferences(private_household=True),
    )

    response = api_client.get(api_routes.explore_groups_group_slug_households(unique_user.group_id))
    if is_private_group:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        response_ids = [item["id"] for item in response.json()["items"]]
        assert str(public_household.id) in response_ids
        assert str(private_household.id) not in response_ids


@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_private_household", [True, False])
def test_get_household(
    api_client: TestClient, unique_user: TestUser, is_private_group: bool, is_private_household: bool
):
    unique_user.repos.group_preferences.patch(UUID(unique_user.group_id), {"private_group": is_private_group})
    household = household = HouseholdService.create_household(
        unique_user.repos,
        HouseholdCreate(name=random_string()),
        CreateHouseholdPreferences(private_household=is_private_household),
    )

    response = api_client.get(
        api_routes.explore_groups_group_slug_households_household_slug(unique_user.group_id, household.slug),
        headers=unique_user.token,
    )

    if is_private_group or is_private_household:
        assert response.status_code == 404
    else:
        assert response.status_code == 200
        assert response.json()["id"] == str(household.id)
