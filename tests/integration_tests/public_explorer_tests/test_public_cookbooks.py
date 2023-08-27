import random

import pytest
from fastapi.testclient import TestClient

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.cookbook.cookbook import SaveCookBook
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_category import TagSave
from tests.utils import api_routes
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


@pytest.mark.parametrize("is_private_group", [True, False], ids=["group_is_private", "group_is_public"])
def test_get_all_cookbooks(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    is_private_group: bool,
):
    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Cookbooks
    default_cookbooks = database.cookbooks.create_many(
        [SaveCookBook(name=random_string(), group_id=unique_user.group_id) for _ in range(random_int(15, 20))]
    )

    random.shuffle(default_cookbooks)
    split_index = random_int(6, 12)
    public_cookbooks = default_cookbooks[:split_index]
    private_cookbooks = default_cookbooks[split_index:]

    for cookbook in public_cookbooks:
        cookbook.public = True

    for cookbook in private_cookbooks:
        cookbook.public = False

    database.cookbooks.update_many(public_cookbooks + private_cookbooks)

    ## Test Cookbooks
    response = api_client.get(api_routes.explore_cookbooks_group_slug(unique_user.group_id))
    if is_private_group:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    cookbooks_data = response.json()
    fetched_ids: set[str] = {cookbook["id"] for cookbook in cookbooks_data["items"]}

    for cookbook in public_cookbooks:
        assert str(cookbook.id) in fetched_ids

    for cookbook in private_cookbooks:
        assert str(cookbook.id) not in fetched_ids


@pytest.mark.parametrize(
    "is_private_group, is_private_cookbook",
    [
        (True, True),
        (True, False),
        (False, True),
        (False, False),
    ],
    ids=[
        "group_is_private_cookbook_is_private",
        "group_is_private_cookbook_is_public",
        "group_is_public_cookbook_is_private",
        "group_is_public_cookbook_is_public",
    ],
)
def test_get_one_cookbook(
    api_client: TestClient,
    unique_user: TestUser,
    database: AllRepositories,
    is_private_group: bool,
    is_private_cookbook: bool,
):
    ## Set Up Group
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = is_private_group
    database.group_preferences.update(group.id, group.preferences)

    ## Set Up Cookbook
    cookbook = database.cookbooks.create(
        SaveCookBook(
            name=random_string(),
            group_id=unique_user.group_id,
            public=not is_private_cookbook,
        )
    )

    ## Test Cookbook
    response = api_client.get(api_routes.explore_cookbooks_group_slug_item_id(unique_user.group_id, cookbook.id))
    if is_private_group or is_private_cookbook:
        assert response.status_code == 404
        return

    assert response.status_code == 200
    cookbook_data = response.json()
    assert cookbook_data["id"] == str(cookbook.id)


def test_get_cookbooks_with_recipes(api_client: TestClient, unique_user: TestUser, database: AllRepositories):
    # Create a public and private recipe with a known tag
    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences

    group.preferences.private_group = False
    database.group_preferences.update(group.id, group.preferences)

    tag = database.tags.create(TagSave(name=random_string(), group_id=unique_user.group_id))
    public_recipe, private_recipe = database.recipes.create_many(
        Recipe(user_id=unique_user.user_id, group_id=unique_user.group_id, name=random_string()) for _ in range(2)
    )

    assert public_recipe.settings
    public_recipe.settings.public = True
    public_recipe.tags = [tag]

    assert private_recipe.settings
    private_recipe.settings.public = False
    private_recipe.tags = [tag]

    database.recipes.update_many([public_recipe, private_recipe])

    # Create a public cookbook with tag
    cookbook = database.cookbooks.create(
        SaveCookBook(name=random_string(), group_id=unique_user.group_id, public=True, tags=[tag])
    )
    database.cookbooks.create(cookbook)

    # Get the cookbook and make sure we only get the public recipe
    response = api_client.get(api_routes.explore_cookbooks_group_slug_item_id(unique_user.group_id, cookbook.id))
    assert response.status_code == 200
    cookbook_data = response.json()
    assert cookbook_data["id"] == str(cookbook.id)

    cookbook_recipe_ids: set[str] = {recipe["id"] for recipe in cookbook_data["recipes"]}
    assert len(cookbook_recipe_ids) == 1
    assert str(public_recipe.id) in cookbook_recipe_ids
    assert str(private_recipe.id) not in cookbook_recipe_ids
