from datetime import datetime, timezone
from uuid import UUID

from dateutil.parser import parse as parse_dt
from fastapi.testclient import TestClient

from mealie.db.models.household import HouseholdToRecipe
from mealie.schema.recipe.recipe import Recipe
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_get_household_members(api_client: TestClient, user_tuple: list[TestUser], h2_user: TestUser):
    usr_1, usr_2 = user_tuple

    response = api_client.get(api_routes.households_members, params={"perPage": -1}, headers=usr_1.token)
    assert response.status_code == 200

    members = response.json()["items"]
    assert len(members) >= 2

    all_ids = [x["id"] for x in members]

    assert str(usr_1.user_id) in all_ids
    assert str(usr_2.user_id) in all_ids
    assert str(h2_user.user_id) not in all_ids


def test_get_household_recipe_default(api_client: TestClient, unique_user: TestUser):
    recipe = unique_user.repos.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=UUID(unique_user.group_id),
            name=random_string(),
        )
    )
    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200
    assert response.json()["recipeId"] == str(recipe.id)
    assert response.json()["lastMade"] is None


def test_get_household_recipe(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    dt_now = datetime.now(tz=timezone.utc)
    recipe = unique_user.repos.recipes.create(
        Recipe(
            user_id=unique_user.user_id,
            group_id=UUID(unique_user.group_id),
            name=random_string(),
        )
    )

    session = unique_user.repos.session
    session.add(
        HouseholdToRecipe(
            session=session,
            household_id=UUID(unique_user.household_id),
            recipe_id=recipe.id,
            last_made=dt_now,
        )
    )
    session.commit()

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=unique_user.token)
    assert response.status_code == 200

    data = response.json()
    assert data["recipeId"] == str(recipe.id)
    assert data["lastMade"]
    assert parse_dt(data["lastMade"]) == dt_now

    response = api_client.get(api_routes.households_self_recipes_recipe_slug(recipe.slug), headers=h2_user.token)
    assert response.status_code == 200

    h2_data = response.json()
    assert h2_data["recipeId"] == str(recipe.id)
    assert h2_data["lastMade"] is None


def test_get_household_recipe_invalid_recipe(api_client: TestClient, unique_user: TestUser):
    response = api_client.get(
        api_routes.households_self_recipes_recipe_slug(random_string()), headers=unique_user.token
    )
    assert response.status_code == 404
