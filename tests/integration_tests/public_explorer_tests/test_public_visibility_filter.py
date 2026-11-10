import pytest
from fastapi.testclient import TestClient

from mealie.schema.cookbook.cookbook import CookBookSave
from mealie.schema.recipe.recipe import RecipeDraft
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser

# Each payload tries to push the appended visibility guard out of the filter, e.g. by opening a
# string or list that swallows it when the combined filter string is parsed again.
BREAKOUT_FILTERS = [
    'id IS NOT NULL " )[',
    'id IS NOT NULL "[',
    'id IS NOT NULL ["',
    "id IS NOT NULL ) OR (id IS NOT NULL",
    "id IS NOT NULL OR (id IS NOT NULL",
    'id IS NOT NULL ") OR (id IS NOT NULL',
    "id IS NOT NULL ) OR ( id IS NOT NULL ) AND (id IS NOT NULL",
    "id IS NOT NULL) OR (id IS NOT NULL",
]


class _Fixture:
    def __init__(self, group_slug: str):
        self.group_slug = group_slug
        self.visible_recipe_ids: set[str] = set()
        self.hidden_recipe_ids: set[str] = set()
        self.visible_cookbook_ids: set[str] = set()
        self.hidden_cookbook_ids: set[str] = set()
        self.visible_household_ids: set[str] = set()
        self.hidden_household_ids: set[str] = set()


@pytest.fixture
def visibility(unique_user: TestUser, h2_user: TestUser) -> _Fixture:
    group = unique_user.repos.groups.get_one(unique_user.group_id)
    assert group and group.preferences
    group.preferences.private_group = False
    unique_user.repos.group_preferences.update(group.id, group.preferences)

    data = _Fixture(group.slug)
    for user, is_private in [(unique_user, False), (h2_user, True)]:
        household = user.repos.households.get_one(user.household_id)
        assert household and household.preferences
        household.preferences.private_household = is_private
        user.repos.household_preferences.update(household.id, household.preferences)
        (data.hidden_household_ids if is_private else data.visible_household_ids).add(str(household.id))

        public_recipe, unlisted_recipe = user.repos.recipes.create_many(
            [RecipeDraft(user_id=user.user_id, group_id=user.group_id, name=random_string()) for _ in range(2)]
        )
        assert public_recipe.settings and unlisted_recipe.settings
        public_recipe.settings.public = True
        unlisted_recipe.settings.public = False
        user.repos.recipes.update_many([public_recipe, unlisted_recipe])
        (data.hidden_recipe_ids if is_private else data.visible_recipe_ids).add(str(public_recipe.id))
        data.hidden_recipe_ids.add(str(unlisted_recipe.id))

        for public in (True, False):
            cookbook = user.repos.cookbooks.create(
                CookBookSave(
                    name=random_string(),
                    group_id=user.group_id,
                    household_id=user.household_id,
                    public=public,
                )
            )
            if public and not is_private:
                data.visible_cookbook_ids.add(str(cookbook.id))
            else:
                data.hidden_cookbook_ids.add(str(cookbook.id))

    return data


def _ids(response) -> set[str]:
    assert response.status_code in (200, 400), response.text
    if response.status_code == 400:
        return set()
    return {item["id"] for item in response.json()["items"]}


@pytest.mark.parametrize("query_filter", BREAKOUT_FILTERS)
def test_public_recipes_filter_cannot_bypass_visibility(
    api_client: TestClient, visibility: _Fixture, query_filter: str
):
    response = api_client.get(
        api_routes.explore_groups_group_slug_recipes(visibility.group_slug),
        params={"queryFilter": query_filter, "perPage": -1},
    )
    assert not _ids(response) & visibility.hidden_recipe_ids


@pytest.mark.parametrize("query_filter", BREAKOUT_FILTERS)
def test_public_recipe_suggestions_filter_cannot_bypass_visibility(
    api_client: TestClient, visibility: _Fixture, query_filter: str
):
    response = api_client.get(
        api_routes.explore_groups_group_slug_recipes_suggestions(visibility.group_slug),
        params={"queryFilter": query_filter, "limit": 100},
    )
    assert response.status_code in (200, 400), response.text
    if response.status_code == 200:
        returned = {item["recipe"]["id"] for item in response.json()["items"]}
        assert not returned & visibility.hidden_recipe_ids


@pytest.mark.parametrize("query_filter", BREAKOUT_FILTERS)
def test_public_cookbooks_filter_cannot_bypass_visibility(
    api_client: TestClient, visibility: _Fixture, query_filter: str
):
    response = api_client.get(
        api_routes.explore_groups_group_slug_cookbooks(visibility.group_slug),
        params={"queryFilter": query_filter, "perPage": -1},
    )
    assert not _ids(response) & visibility.hidden_cookbook_ids


@pytest.mark.parametrize("query_filter", BREAKOUT_FILTERS)
def test_public_households_filter_cannot_bypass_visibility(
    api_client: TestClient, visibility: _Fixture, query_filter: str
):
    response = api_client.get(
        api_routes.explore_groups_group_slug_households(visibility.group_slug),
        params={"queryFilter": query_filter, "perPage": -1},
    )
    assert not _ids(response) & visibility.hidden_household_ids


def test_public_listings_still_return_visible_items(api_client: TestClient, visibility: _Fixture):
    slug = visibility.group_slug
    params = {"perPage": -1}

    recipe_ids = _ids(api_client.get(api_routes.explore_groups_group_slug_recipes(slug), params=params))
    assert visibility.visible_recipe_ids <= recipe_ids
    assert not recipe_ids & visibility.hidden_recipe_ids

    cookbook_ids = _ids(api_client.get(api_routes.explore_groups_group_slug_cookbooks(slug), params=params))
    assert visibility.visible_cookbook_ids <= cookbook_ids
    assert not cookbook_ids & visibility.hidden_cookbook_ids

    household_ids = _ids(api_client.get(api_routes.explore_groups_group_slug_households(slug), params=params))
    assert visibility.visible_household_ids <= household_ids
    assert not household_ids & visibility.hidden_household_ids

    filtered = _ids(
        api_client.get(
            api_routes.explore_groups_group_slug_recipes(slug), params={**params, "queryFilter": "id IS NOT NULL"}
        )
    )
    assert visibility.visible_recipe_ids <= filtered
    assert not filtered & visibility.hidden_recipe_ids
