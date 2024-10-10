import random

import pytest
from fastapi.testclient import TestClient
from pydantic import UUID4

from mealie.schema.cookbook.cookbook import ReadCookBook, SaveCookBook
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_category import TagSave
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_household_1_private", [True, False])
@pytest.mark.parametrize("is_household_2_private", [True, False])
def test_get_all_cookbooks(
    api_client: TestClient,
    unique_user: TestUser,
    h2_user: TestUser,
    is_private_group: bool,
    is_household_1_private: bool,
    is_household_2_private: bool,
):
    ## Set Up Group
    group = unique_user.repos.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    unique_user.repos.group_preferences.update(group.id, group.preferences)

    ## Set Up Household and Cookbooks
    household_private_map: dict[UUID4, bool] = {}
    public_cookbooks: list[ReadCookBook] = []
    private_cookbooks: list[ReadCookBook] = []
    for user, is_private_household in [
        (unique_user, is_household_1_private),
        (h2_user, is_household_2_private),
    ]:
        database = user.repos
        household = database.households.get_one(user.household_id)
        assert household and household.preferences

        household_private_map[household.id] = is_private_household
        household.preferences.private_household = is_private_household
        household.preferences.recipe_public = not is_private_household
        database.household_preferences.update(household.id, household.preferences)

        ## Set Up Cookbooks
        default_cookbooks = database.cookbooks.create_many(
            [
                SaveCookBook(name=random_string(), group_id=user.group_id, household_id=user.household_id)
                for _ in range(random_int(15, 20))
            ]
        )

        random.shuffle(default_cookbooks)
        split_index = random_int(6, 12)
        public_cookbooks.extend(default_cookbooks[:split_index])
        private_cookbooks.extend(default_cookbooks[split_index:])

        for cookbook in default_cookbooks[:split_index]:
            cookbook.public = True

        for cookbook in default_cookbooks[split_index:]:
            cookbook.public = False

        database.cookbooks.update_many(default_cookbooks)

    ## Test Cookbooks
    response = api_client.get(api_routes.explore_groups_group_slug_cookbooks(unique_user.group_id))
    if is_private_group:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    cookbooks_data = response.json()
    fetched_ids: set[str] = {cookbook["id"] for cookbook in cookbooks_data["items"]}

    for cookbook in public_cookbooks:
        is_private_household = household_private_map[cookbook.household_id]
        if is_private_household:
            assert str(cookbook.id) not in fetched_ids
        else:
            assert str(cookbook.id) in fetched_ids

    for cookbook in private_cookbooks:
        assert str(cookbook.id) not in fetched_ids


@pytest.mark.parametrize("is_private_group", [True, False])
@pytest.mark.parametrize("is_private_household", [True, False])
@pytest.mark.parametrize("is_private_cookbook", [True, False])
def test_get_one_cookbook(
    api_client: TestClient,
    unique_user: TestUser,
    is_private_group: bool,
    is_private_household: bool,
    is_private_cookbook: bool,
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

    ## Set Up Cookbook
    cookbook = database.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            public=not is_private_cookbook,
        )
    )

    ## Test Cookbook
    response = api_client.get(api_routes.explore_groups_group_slug_cookbooks_item_id(unique_user.group_id, cookbook.id))
    if is_private_group or is_private_household or is_private_cookbook:
        assert response.status_code == 404
        if is_private_group:
            assert response.json()["detail"] == "group not found"
        else:
            assert response.json()["detail"] == "cookbook not found"
        return

    assert response.status_code == 200
    cookbook_data = response.json()
    assert cookbook_data["id"] == str(cookbook.id)


def test_get_cookbooks_with_recipes(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    database = unique_user.repos

    # Create a public and private recipe with a known tag
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = False
    database.group_preferences.update(group.id, group.preferences)

    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = False
    household.preferences.recipe_public = True
    database.household_preferences.update(household.id, household.preferences)

    tag = database.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    public_recipe, private_recipe = database.recipes.create_many(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=random_string(),
        )
        for _ in range(2)
    )

    assert public_recipe.settings
    public_recipe.settings.public = True
    public_recipe.tags = [tag]

    assert private_recipe.settings
    private_recipe.settings.public = False
    private_recipe.tags = [tag]

    database.recipes.update_many([public_recipe, private_recipe])

    # Create a public and private recipe with a known tag in another household
    other_database = h2_user.repos
    other_household = other_database.households.get_one(h2_user.household_id)
    assert other_household and other_household.preferences

    other_household.preferences.private_household = False
    other_household.preferences.recipe_public = True
    other_database.household_preferences.update(household.id, household.preferences)

    other_household_public_recipe, other_household_private_recipe = database.recipes.create_many(
        Recipe(
            user_id=h2_user.user_id,
            group_id=h2_user.group_id,
            name=random_string(),
        )
        for _ in range(2)
    )

    assert other_household_public_recipe.settings
    other_household_public_recipe.settings.public = True
    other_household_public_recipe.tags = [tag]

    assert other_household_private_recipe.settings
    other_household_private_recipe.settings.public = False
    other_household_private_recipe.tags = [tag]

    other_database.recipes.update_many([other_household_public_recipe, other_household_private_recipe])

    # Create a public cookbook with tag
    cookbook = database.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            public=True,
            query_filter_string=f'tags.id IN ["{tag.id}"]',
        )
    )

    # Get the cookbook and make sure we only get the public recipes from each household
    response = api_client.get(api_routes.explore_groups_group_slug_cookbooks_item_id(unique_user.group_id, cookbook.id))
    assert response.status_code == 200
    cookbook_data = response.json()
    assert cookbook_data["id"] == str(cookbook.id)

    cookbook_recipe_ids: set[str] = {recipe["id"] for recipe in cookbook_data["recipes"]}
    assert len(cookbook_recipe_ids) == 2
    assert str(public_recipe.id) in cookbook_recipe_ids
    assert str(private_recipe.id) not in cookbook_recipe_ids
    assert str(other_household_public_recipe.id) in cookbook_recipe_ids
    assert str(other_household_private_recipe.id) not in cookbook_recipe_ids


def test_get_cookbooks_private_household(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    database = unique_user.repos

    # Create a public recipe with a known tag
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = False
    database.group_preferences.update(group.id, group.preferences)

    household = database.households.get_one(unique_user.household_id)
    assert household and household.preferences

    household.preferences.private_household = False
    household.preferences.recipe_public = True
    database.household_preferences.update(household.id, household.preferences)

    tag = database.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    public_recipe = database.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=unique_user.group_id,
            name=random_string(),
        )
    )

    assert public_recipe.settings
    public_recipe.settings.public = True
    public_recipe.tags = [tag]

    database.recipes.update(public_recipe.slug, public_recipe)

    # Create a public recipe with a known tag on a private household
    other_database = h2_user.repos
    other_household = other_database.households.get_one(h2_user.household_id)
    assert other_household and other_household.preferences

    other_household.preferences.private_household = True
    other_household.preferences.recipe_public = True
    other_database.household_preferences.update(household.id, household.preferences)

    other_household_private_recipe = database.recipes.create(
        Recipe(
            user_id=h2_user.user_id,
            group_id=h2_user.group_id,
            name=random_string(),
        )
    )

    assert other_household_private_recipe.settings
    other_household_private_recipe.settings.public = False
    other_household_private_recipe.tags = [tag]

    other_database.recipes.update(other_household_private_recipe.slug, other_household_private_recipe)

    # Create a public cookbook with tag
    cookbook = database.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=unique_user.group_id,
            household_id=unique_user.household_id,
            public=True,
            query_filter_string=f'tags.id IN ["{tag.id}"]',
        )
    )

    # Get the cookbook and make sure we only get the public recipes from each household
    response = api_client.get(api_routes.explore_groups_group_slug_cookbooks_item_id(unique_user.group_id, cookbook.id))
    assert response.status_code == 200
    cookbook_data = response.json()
    assert cookbook_data["id"] == str(cookbook.id)

    cookbook_recipe_ids: set[str] = {recipe["id"] for recipe in cookbook_data["recipes"]}
    assert len(cookbook_recipe_ids) == 1
    assert str(public_recipe.id) in cookbook_recipe_ids
    assert str(other_household_private_recipe.id) not in cookbook_recipe_ids
