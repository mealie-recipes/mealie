from enum import Enum

import pytest
from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_category import CategorySave, TagSave
from mealie.schema.recipe.recipe_tool import RecipeToolSave
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


class OrganizerType(Enum):
    categories = "categories"
    tags = "tags"
    tools = "tools"


@pytest.mark.parametrize("organizer_type", [OrganizerType.categories, OrganizerType.tags, OrganizerType.tools])
@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_private_household", [True, False])
def test_get_all_organizers(
    api_client: TestClient,
    unique_user: TestUser,
    organizer_type: OrganizerType,
    is_private_group: bool,
    is_private_household: bool,
):
    database = unique_user.repos

    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Household
    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = is_private_household
    household.preferences.recipe_public = not is_private_household
    database.household_preferences.update(household.id, household.preferences)

    ## Set Up Organizers
    if organizer_type is OrganizerType.categories:
        item_class = CategorySave
        repo = database.categories  # type: ignore
        route = api_routes.explore_groups_group_slug_organizers_categories
    elif organizer_type is OrganizerType.tags:
        item_class = TagSave
        repo = database.tags  # type: ignore
        route = api_routes.explore_groups_group_slug_organizers_tags
    else:
        item_class = RecipeToolSave
        repo = database.tools  # type: ignore
        route = api_routes.explore_groups_group_slug_organizers_tools

    organizers = repo.create_many(
        [item_class(name=random_string(), group_id=unique_user.group_id) for _ in range(random_int(15, 20))]
    )

    ## Test Organizers
    response = api_client.get(route(unique_user.group_id))

    # whether or not the household is private shouldn't affect food visibility
    if is_private_group:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    organizers_data = response.json()
    fetched_ids: set[str] = {organizer["id"] for organizer in organizers_data["items"]}

    for organizer in organizers:
        assert str(organizer.id) in fetched_ids


@pytest.mark.parametrize("organizer_type", [OrganizerType.categories, OrganizerType.tags, OrganizerType.tools])
@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_private_household", [True, False])
def test_get_one_organizer(
    api_client: TestClient,
    unique_user: TestUser,
    organizer_type: OrganizerType,
    is_private_group: bool,
    is_private_household: bool,
):
    database = unique_user.repos

    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Household
    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = is_private_household
    household.preferences.recipe_public = not is_private_household
    database.household_preferences.update(household.id, household.preferences)

    ## Set Up Organizer
    if organizer_type is OrganizerType.categories:
        item_class = CategorySave
        repo = database.categories  # type: ignore
        route = api_routes.explore_groups_group_slug_organizers_categories_item_id
    elif organizer_type is OrganizerType.tags:
        item_class = TagSave
        repo = database.tags  # type: ignore
        route = api_routes.explore_groups_group_slug_organizers_tags_item_id
    else:
        item_class = RecipeToolSave
        repo = database.tools  # type: ignore
        route = api_routes.explore_groups_group_slug_organizers_tools_item_id

    organizer = repo.create(item_class(name=random_string(), group_id=unique_user.group_id))

    ## Test Organizer
    response = api_client.get(route(unique_user.group_id, organizer.id))

    # whether or not the household is private shouldn't affect food visibility
    if is_private_group:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    organizer_data = response.json()
    assert organizer_data["id"] == str(organizer.id)
