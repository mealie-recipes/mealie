from datetime import UTC, datetime
from uuid import UUID, uuid4

from dateutil.parser import parse as parse_dt
from fastapi.testclient import TestClient

from mealie.db.models.household import HouseholdToRecipe
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import IngredientFood, SaveIngredientFood
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_get_household_members(api_client: TestClient, user_tuple: list[TestUser], h2_user: TestUser):
    usr_1, usr_2 = user_tuple

    user = usr_1.repos.users.get_one(usr_1.user_id)
    user.can_manage = True
    usr_1.repos.users.update(user.id, user)

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
    dt_now = datetime.now(tz=UTC)
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


def test_get_household_statistics(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    def get_statistics(user: TestUser) -> dict:
        response = api_client.get(api_routes.households_statistics, headers=user.token)
        assert response.status_code == 200
        return response.json()

    before = get_statistics(unique_user)
    h2_before = get_statistics(h2_user)

    unique_user.repos.recipes.create(
        Recipe(user_id=unique_user.user_id, group_id=UUID(unique_user.group_id), name=random_string())
    )

    after = get_statistics(unique_user)
    h2_after = get_statistics(h2_user)
    assert after["totalRecipes"] == before["totalRecipes"] + 1
    assert h2_after["totalRecipes"] == h2_before["totalRecipes"]


def _create_food(user: TestUser) -> IngredientFood:
    return user.repos.ingredient_foods.create(SaveIngredientFood(name=random_string(), group_id=user.group_id))


def _household_slug(api_client: TestClient, user: TestUser) -> str:
    response = api_client.get(api_routes.households_self, headers=user.token)
    assert response.status_code == 200
    return response.json()["slug"]


def _households_with_food(api_client: TestClient, user: TestUser, food: IngredientFood) -> list[str]:
    response = api_client.get(api_routes.foods_item_id(food.id), headers=user.token)
    assert response.status_code == 200
    return response.json()["householdsWithIngredientFood"]


def test_add_foods_on_hand(api_client: TestClient, unique_user: TestUser):
    foods = [_create_food(unique_user), _create_food(unique_user)]

    response = api_client.post(
        api_routes.households_self_foods_on_hand, json=[str(food.id) for food in foods], headers=unique_user.token
    )
    assert response.status_code == 200

    slug = _household_slug(api_client, unique_user)
    for food in foods:
        assert _households_with_food(api_client, unique_user, food) == [slug]


def test_add_foods_on_hand_keeps_other_households(api_client: TestClient, unique_user: TestUser, h2_user: TestUser):
    food = _create_food(unique_user)
    payload = [str(food.id)]

    response = api_client.post(api_routes.households_self_foods_on_hand, json=payload, headers=unique_user.token)
    assert response.status_code == 200

    # adding a food the household already has on hand is a no-op, not an error
    for _ in range(2):
        response = api_client.post(api_routes.households_self_foods_on_hand, json=payload, headers=h2_user.token)
        assert response.status_code == 200

    assert sorted(_households_with_food(api_client, unique_user, food)) == sorted(
        [_household_slug(api_client, unique_user), _household_slug(api_client, h2_user)]
    )


def test_add_foods_on_hand_without_organize_permission(
    api_client: TestClient, unique_user: TestUser, unprivileged_user: TestUser
):
    food = _create_food(unique_user)

    response = api_client.post(
        api_routes.households_self_foods_on_hand, json=[str(food.id)], headers=unprivileged_user.token
    )
    assert response.status_code == 200
    assert _households_with_food(api_client, unique_user, food) == [_household_slug(api_client, unique_user)]


def test_add_foods_on_hand_rejects_other_group_food(api_client: TestClient, unique_user: TestUser, g2_user: TestUser):
    food = _create_food(unique_user)

    response = api_client.post(api_routes.households_self_foods_on_hand, json=[str(food.id)], headers=g2_user.token)
    assert response.status_code == 404
    assert _households_with_food(api_client, unique_user, food) == []


def test_add_foods_on_hand_is_all_or_nothing(api_client: TestClient, unique_user: TestUser):
    food = _create_food(unique_user)

    response = api_client.post(
        api_routes.households_self_foods_on_hand, json=[str(food.id), str(uuid4())], headers=unique_user.token
    )
    assert response.status_code == 404
    assert _households_with_food(api_client, unique_user, food) == []


def test_add_foods_on_hand_empty_list(api_client: TestClient, unique_user: TestUser):
    response = api_client.post(api_routes.households_self_foods_on_hand, json=[], headers=unique_user.token)
    assert response.status_code == 200
