from fastapi.testclient import TestClient

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    RecipeIngredient,
    SaveIngredientUnit,
    StandardizedUnitType,
)
from mealie.schema.recipe.recipe_step import RecipeStep
from mealie.schema.recipe.unit_system import UnitSystem
from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def _conversions_url(slug: str) -> str:
    return api_routes.recipes_slug_conversions(slug)


def _make_recipe_with_units(
    unique_user: TestUser,
    *,
    quantity: float = 2,
    standard_unit: StandardizedUnitType = StandardizedUnitType.CUP,
    standard_quantity: float = 1,
    instruction_text: str = "Bake at 350°F for 30 minutes.",
) -> Recipe:
    database = unique_user.repos
    unit = database.ingredient_units.create(
        SaveIngredientUnit(
            group_id=unique_user.group_id,
            name=random_string(8),
            standard_quantity=standard_quantity,
            standard_unit=standard_unit.value,
        )
    )
    recipe = Recipe(
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=random_string(10),
        recipe_ingredient=[
            RecipeIngredient(
                quantity=quantity,
                unit=unit,
                note="flour",
            ),
        ],
        recipe_instructions=[RecipeStep(text=instruction_text)],
    )
    return database.recipes.create(recipe)


def test_unauthenticated_returns_401(api_client: TestClient) -> None:
    response = api_client.get(_conversions_url("any-slug"))
    assert response.status_code == 401


def test_unknown_recipe_returns_404(api_client: TestClient, unique_user: TestUser) -> None:
    response = api_client.get(
        _conversions_url("recipe-that-does-not-exist"),
        headers=unique_user.token,
        params={"system": UnitSystem.METRIC.value},
    )
    assert response.status_code == 404


def test_invalid_system_returns_422(api_client: TestClient, unique_user: TestUser) -> None:
    recipe = _make_recipe_with_units(unique_user)
    response = api_client.get(
        _conversions_url(recipe.slug),
        headers=unique_user.token,
        params={"system": "klingon"},
    )
    assert response.status_code == 422


def test_original_returns_input_recipe_unchanged(api_client: TestClient, unique_user: TestUser) -> None:
    recipe = _make_recipe_with_units(unique_user)
    response = api_client.get(
        _conversions_url(recipe.slug),
        headers=unique_user.token,
        params={"system": UnitSystem.ORIGINAL.value},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["recipeIngredient"]) == 1
    assert body["recipeIngredient"][0]["quantity"] == 2
    assert body["recipeInstructions"][0]["text"] == "Bake at 350°F for 30 minutes."


def test_metric_conversion_round_trip(api_client: TestClient, unique_user: TestUser) -> None:
    recipe = _make_recipe_with_units(
        unique_user,
        quantity=2,
        standard_unit=StandardizedUnitType.CUP,
    )
    response = api_client.get(
        _conversions_url(recipe.slug),
        headers=unique_user.token,
        params={"system": UnitSystem.METRIC.value},
    )
    assert response.status_code == 200
    body = response.json()
    ingredient = body["recipeIngredient"][0]
    assert ingredient["unit"]["abbreviation"] == "ml"
    # 2 cups (Pint default = 236.59 ml) → 473.18 ml
    assert abs(ingredient["quantity"] - 473.18) < 0.01
    # 350°F → 177°C
    assert "177°C" in body["recipeInstructions"][0]["text"]


def test_us_conversion_round_trip(api_client: TestClient, unique_user: TestUser) -> None:
    recipe = _make_recipe_with_units(
        unique_user,
        quantity=200,
        standard_unit=StandardizedUnitType.GRAM,
        instruction_text="Bake at 180°C.",
    )
    response = api_client.get(
        _conversions_url(recipe.slug),
        headers=unique_user.token,
        params={"system": UnitSystem.US.value},
    )
    assert response.status_code == 200
    body = response.json()
    ingredient = body["recipeIngredient"][0]
    # 200g → ~7.05 oz (less than 1 lb)
    assert ingredient["unit"]["abbreviation"] == "oz"
    assert abs(ingredient["quantity"] - 7.05) < 0.1
    # 180°C → 356°F
    assert "356°F" in body["recipeInstructions"][0]["text"]


def test_imperial_conversion_round_trip(api_client: TestClient, unique_user: TestUser) -> None:
    recipe = _make_recipe_with_units(
        unique_user,
        quantity=1000,
        standard_unit=StandardizedUnitType.MILLILITER,
        instruction_text="Heat to 100°F.",
    )
    response = api_client.get(
        _conversions_url(recipe.slug),
        headers=unique_user.token,
        params={"system": UnitSystem.IMPERIAL.value},
    )
    assert response.status_code == 200
    body = response.json()
    ingredient = body["recipeIngredient"][0]
    # 1000 ml → ~1.76 imperial pints
    assert ingredient["unit"]["abbreviation"] == "pt"
    assert abs(ingredient["quantity"] - 1.76) < 0.01
    # 100°F → 38°C (imperial uses Celsius, like metric)
    assert "38°C" in body["recipeInstructions"][0]["text"]


def test_recipe_without_unit_is_passed_through(api_client: TestClient, unique_user: TestUser) -> None:
    """An ingredient with no unit (just a note like "a pinch of salt") shouldn't crash."""
    database = unique_user.repos
    recipe = Recipe(
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=random_string(10),
        recipe_ingredient=[RecipeIngredient(quantity=1, note="A pinch of salt")],
        recipe_instructions=[RecipeStep(text="Mix together.")],
    )
    created = database.recipes.create(recipe)

    response = api_client.get(
        _conversions_url(created.slug),
        headers=unique_user.token,
        params={"system": UnitSystem.METRIC.value},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["recipeIngredient"][0]["note"] == "A pinch of salt"
