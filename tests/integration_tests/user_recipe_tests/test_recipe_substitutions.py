from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe_ingredient import CreateIngredientFood, SaveIngredientFood
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def create_food(user: TestUser, api_client: TestClient, substitutions: list[dict] | None = None) -> dict:
    data = CreateIngredientFood(name=random_string(10)).model_dump(by_alias=True)
    data["substitutions"] = substitutions or []

    response = api_client.post(api_routes.foods, json=data, headers=user.token)
    assert response.status_code == 201
    return response.json()


def get_food(user: TestUser, api_client: TestClient, food_id: str) -> dict:
    response = api_client.get(api_routes.foods_item_id(food_id), headers=user.token)
    assert response.status_code == 200
    return response.json()


def update_food(user: TestUser, api_client: TestClient, food: dict, substitutions: list[dict]) -> dict:
    payload = {"id": food["id"], "name": food["name"], "substitutions": substitutions}
    response = api_client.put(api_routes.foods_item_id(food["id"]), json=payload, headers=user.token)
    assert response.status_code == 200
    return response.json()


def create_recipe_with_substitutions(user: TestUser, api_client: TestClient, substitutions: list[dict]) -> dict:
    """Creates a recipe with one ingredient carrying the given substitutions, and returns it."""

    response = api_client.post(api_routes.recipes, json={"name": random_string()}, headers=user.token)
    assert response.status_code == 201
    slug = response.json()

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=user.token).json()
    recipe["recipeIngredient"] = [{"note": random_string(), "substitutions": substitutions}]

    response = api_client.put(api_routes.recipes_slug(slug), json=recipe, headers=user.token)
    assert response.status_code == 200

    return api_client.get(api_routes.recipes_slug(slug), headers=user.token).json()


def test_food_substitutions_round_trip_all_three_forms(api_client: TestClient, unique_user: TestUser):
    substitute = create_food(unique_user, api_client)
    with_note = create_food(unique_user, api_client)

    food = create_food(
        unique_user,
        api_client,
        substitutions=[
            {"substituteFoodId": substitute["id"]},
            {"substituteFoodId": with_note["id"], "note": "1 tbsp vinegar per cup"},
            {"note": "water and a bouillon cube"},
        ],
    )

    stored = get_food(unique_user, api_client, food["id"])["substitutions"]
    assert len(stored) == 3

    by_food_id = {sub["substituteFoodId"]: sub for sub in stored}

    assert by_food_id[substitute["id"]]["note"] is None
    assert by_food_id[substitute["id"]]["substituteFood"]["name"] == substitute["name"]

    assert by_food_id[with_note["id"]]["note"] == "1 tbsp vinegar per cup"
    assert by_food_id[with_note["id"]]["substituteFood"]["name"] == with_note["name"]

    assert by_food_id[None]["note"] == "water and a bouillon cube"
    assert by_food_id[None]["substituteFood"] is None


def test_food_update_preserves_an_untouched_substitution(api_client: TestClient, unique_user: TestUser):
    """
    Adding a substitution while keeping an existing one is the most ordinary edit there is.
    Rebuilding the rows from scratch re-inserts the unchanged one before the old copy is
    deleted, which trips the (food_id, substitute_food_id) constraint.
    """

    first = create_food(unique_user, api_client)
    second = create_food(unique_user, api_client)
    food = create_food(unique_user, api_client, substitutions=[{"substituteFoodId": first["id"]}])

    update_food(
        unique_user,
        api_client,
        food,
        [{"substituteFoodId": first["id"]}, {"substituteFoodId": second["id"]}],
    )

    stored = get_food(unique_user, api_client, food["id"])["substitutions"]
    assert {sub["substituteFoodId"] for sub in stored} == {first["id"], second["id"]}


def test_food_update_can_clear_substitutions(api_client: TestClient, unique_user: TestUser):
    substitute = create_food(unique_user, api_client)
    food = create_food(unique_user, api_client, substitutions=[{"substituteFoodId": substitute["id"]}])

    update_food(unique_user, api_client, food, [])

    assert get_food(unique_user, api_client, food["id"])["substitutions"] == []


def test_food_update_can_replace_a_substitution(api_client: TestClient, unique_user: TestUser):
    first = create_food(unique_user, api_client)
    second = create_food(unique_user, api_client)
    food = create_food(unique_user, api_client, substitutions=[{"substituteFoodId": first["id"]}])

    update_food(unique_user, api_client, food, [{"substituteFoodId": second["id"]}])

    stored = get_food(unique_user, api_client, food["id"])["substitutions"]
    assert [sub["substituteFoodId"] for sub in stored] == [second["id"]]


def test_self_substitution_is_rejected(api_client: TestClient, unique_user: TestUser):
    food = create_food(unique_user, api_client)

    payload = {"id": food["id"], "name": food["name"], "substitutions": [{"substituteFoodId": food["id"]}]}
    response = api_client.put(api_routes.foods_item_id(food["id"]), json=payload, headers=unique_user.token)

    assert response.status_code == 422


def test_substitute_food_from_another_group_is_dropped(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
):
    """
    Substitute ids are user-supplied and aren't covered by the repository's group scoping. An
    id belonging to another group must be dropped rather than linked or created, or its name
    leaks through every recipe page that renders the substitution.
    """

    foreign_food = g2_user.repos.ingredient_foods.create(
        SaveIngredientFood(name=random_string(10), group_id=g2_user.group_id)
    )

    food = create_food(
        unique_user,
        api_client,
        substitutions=[
            {"substituteFoodId": str(foreign_food.id), "note": "a note that goes with it"},
            {"note": "a standalone note"},
        ],
    )

    stored = get_food(unique_user, api_client, food["id"])["substitutions"]

    # the note qualified the food it travelled with, so the whole substitution goes
    assert len(stored) == 1
    assert stored[0]["substituteFoodId"] is None
    assert stored[0]["note"] == "a standalone note"

    # and nothing was manufactured in this group to satisfy the id
    assert unique_user.repos.ingredient_foods.get_one(foreign_food.id) is None


def test_recipe_substitutions_survive_a_resave(api_client: TestClient, unique_user: TestUser):
    """
    Ingredient rows are destroyed and recreated on every recipe save, with their integer PKs
    reallocated. Substitutions must be rebuilt with them rather than left pointing at rows
    that no longer exist.
    """

    substitute = create_food(unique_user, api_client)
    recipe = create_recipe_with_substitutions(
        unique_user,
        api_client,
        [{"substituteFoodId": substitute["id"], "note": "pork works"}, {"note": "or use tofu"}],
    )

    stored = recipe["recipeIngredient"][0]["substitutions"]
    assert len(stored) == 2

    # save the recipe straight back, exactly as the editor would
    response = api_client.put(api_routes.recipes_slug(recipe["slug"]), json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    reloaded = api_client.get(api_routes.recipes_slug(recipe["slug"]), headers=unique_user.token).json()
    resaved = reloaded["recipeIngredient"][0]["substitutions"]

    assert len(resaved) == 2
    assert resaved[0]["substituteFoodId"] == substitute["id"]
    assert resaved[0]["substituteFood"]["name"] == substitute["name"]
    assert resaved[0]["note"] == "pork works"
    assert resaved[1]["substituteFoodId"] is None
    assert resaved[1]["note"] == "or use tofu"


def test_recipe_substitute_food_from_another_group_is_dropped(
    api_client: TestClient, unique_user: TestUser, g2_user: TestUser
):
    foreign_food = g2_user.repos.ingredient_foods.create(
        SaveIngredientFood(name=random_string(10), group_id=g2_user.group_id)
    )

    recipe = create_recipe_with_substitutions(
        unique_user, api_client, [{"substituteFoodId": str(foreign_food.id)}, {"note": "a standalone note"}]
    )

    stored = recipe["recipeIngredient"][0]["substitutions"]
    assert len(stored) == 1
    assert stored[0]["note"] == "a standalone note"


def test_recipe_duplicate_carries_substitutions(api_client: TestClient, unique_user: TestUser):
    substitute = create_food(unique_user, api_client)
    recipe = create_recipe_with_substitutions(
        unique_user, api_client, [{"substituteFoodId": substitute["id"], "note": "pork works"}]
    )

    response = api_client.post(
        api_routes.recipes_slug_duplicate(recipe["slug"]), json={"name": random_string()}, headers=unique_user.token
    )
    assert response.status_code == 201

    duplicate = api_client.get(api_routes.recipes_slug(response.json()["slug"]), headers=unique_user.token).json()
    assert duplicate["id"] != recipe["id"]

    copied = duplicate["recipeIngredient"][0]["substitutions"]
    assert len(copied) == 1
    assert copied[0]["substituteFoodId"] == substitute["id"]
    assert copied[0]["note"] == "pork works"


def test_explore_foods_include_substitutions(api_client: TestClient, unique_user: TestUser):
    database = unique_user.repos

    group = database.groups.get_one(unique_user.group_id)
    assert group and group.preferences
    group.preferences.private_group = False
    database.group_preferences.update(group.id, group.preferences)

    substitute = create_food(unique_user, api_client)
    food = create_food(unique_user, api_client, substitutions=[{"substituteFoodId": substitute["id"]}])

    response = api_client.get(api_routes.explore_groups_group_slug_foods_item_id(unique_user.group_id, food["id"]))
    assert response.status_code == 200

    stored = response.json()["substitutions"]
    assert len(stored) == 1
    assert stored[0]["substituteFoodId"] == substitute["id"]
    assert stored[0]["substituteFood"]["name"] == substitute["name"]
