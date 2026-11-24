from typing import Any
from uuid import uuid4

import pytest

from mealie.schema.recipe import RecipeSummary
from mealie.schema.recipe.recipe import RecipeDraft, RecipeOut
from mealie.schema.recipe.recipe_nutrition import Nutrition
from mealie.schema.recipe.recipe_settings import RecipeSettings

SHOULD_ERROR = "this_test_should_error"


@pytest.mark.parametrize("field", ["tags", "recipe_category", "tools"])
def test_recipe_organizer_string_list_coercion(field: str):
    """Regression test for #6887: a plain string list for tags/recipeCategory/tools
    (as opposed to a list of {"name": ...} objects) must be coerced into real
    organizer objects rather than rejected or silently dropped. `tools` previously
    lacked this coercion entirely, unlike `tags`/`recipe_category`.

    The before-validators live on `RecipeDraft` (not `RecipeSummary`, despite the fields
    themselves being declared there), matching where the actual API route validates
    incoming data.
    """
    recipe = RecipeDraft(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        name="test",
        **{field: ["Ramen", "Japanese"]},
    )

    organizers = getattr(recipe, field)
    assert organizers is not None
    assert [o.name for o in organizers] == ["Ramen", "Japanese"]
    assert [o.slug for o in organizers] == ["ramen", "japanese"]


@pytest.mark.parametrize("field", ["recipe_servings", "recipe_yield_quantity"])
@pytest.mark.parametrize(
    ["val", "expected"],
    [
        (0, 0),
        (None, 0),
        ("", 0),
        (10, 10),
        (2.25, 2.25),
        ("10", 10),
        ("invalid", SHOULD_ERROR),
    ],
)
def test_recipe_number_sanitation(field: str, val: Any, expected: Any):
    try:
        recipe = RecipeDraft(
            id=uuid4(),
            user_id=uuid4(),
            household_id=uuid4(),
            group_id=uuid4(),
            **{field: val},
        )
    except ValueError:
        if expected == SHOULD_ERROR:
            return
        else:
            raise

    assert expected != SHOULD_ERROR, "Value should have errored"
    assert getattr(recipe, field) == expected


@pytest.mark.parametrize("field", ["total_time_seconds", "prep_time_seconds", "perform_time_seconds"])
@pytest.mark.parametrize(
    ["val", "expected"],
    [
        (None, None),
        (0, 0),
        (5400, 5400),
        (2**31 - 1, 2**31 - 1),
        # Past the Postgres INTEGER max, which SQLite would have accepted
        (2**31, SHOULD_ERROR),
        (-1, SHOULD_ERROR),
    ],
)
def test_recipe_duration_bounds(field: str, val: Any, expected: Any):
    try:
        recipe = RecipeDraft(
            id=uuid4(),
            user_id=uuid4(),
            household_id=uuid4(),
            group_id=uuid4(),
            **{field: val},
        )
    except ValueError:
        if expected == SHOULD_ERROR:
            return
        else:
            raise

    assert expected != SHOULD_ERROR, "Value should have errored"
    assert getattr(recipe, field) == expected


@pytest.mark.parametrize("field", ["recipe_yield", "total_time", "prep_time", "perform_time"])
@pytest.mark.parametrize(
    ["val", "expected"],
    [
        ("normal string", "normal string"),
        ("", ""),
        (None, None),
        (10, "10"),
        (2.25, "2.25"),
    ],
)
def test_recipe_string_sanitation(field: str, val: Any, expected: Any):
    recipe = RecipeDraft(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        **{field: val},
    )

    assert getattr(recipe, field) == expected


@pytest.mark.parametrize(
    ["recipe_yield_quantity", "recipe_yield", "recipe_servings", "expected"],
    [
        # Explicit yield quantity + text
        (8, "slices", 0, "8 slices"),
        # Whole-number quantities render without a trailing ".0"
        (8, "servings", 0, "8 servings"),
        # Fractional quantities are preserved
        (2.25, "loaves", 0, "2.25 loaves"),
        # Yield text only, no quantity
        (0, "a dozen cookies", 0, "a dozen cookies"),
        # Yield text only, with servings set: servings don't get prefixed onto the text
        (0, "a dozen cookies", 4, "a dozen cookies"),
        # Servings-only recipe: falls back to recipe_servings instead of "0.0"
        (0, None, 4, "4"),
        (0, "", 4, "4"),
        # Nothing set at all
        (0, None, 0, ""),
    ],
)
def test_recipe_yield_display(
    recipe_yield_quantity: float,
    recipe_yield: str | None,
    recipe_servings: float,
    expected: str,
):
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        name="Bread",
        slug="bread",
        recipe_yield_quantity=recipe_yield_quantity,
        recipe_yield=recipe_yield,
        recipe_servings=recipe_servings,
    )

    assert recipe.recipe_yield_display == expected


def test_recipe_preserves_existing_slug():
    recipe = RecipeDraft(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        name="Bols nourrissants (copie de Zuppa)",
        slug="nourish-bowls-zuppa-copycat",
    )

    assert recipe.slug == "nourish-bowls-zuppa-copycat"


@pytest.mark.parametrize(
    ["payload", "expected"],
    [
        ({"cookTime": "20 minutes"}, "20 minutes"),
        ({"cook_time": "20 minutes"}, "20 minutes"),
        ({"cookTime": "1 hour", "performTime": "20 minutes"}, "20 minutes"),
        ({"cookTime": "1 hour", "performTimeSeconds": 1200}, None),
        ({"cookTime": None}, None),
    ],
)
def test_recipe_legacy_cook_time_input(payload: dict[str, Any], expected: str | None):
    recipe = RecipeDraft.model_validate({"name": "Soup", **payload})

    assert recipe.perform_time == expected
    assert "cookTime" not in recipe.model_dump(by_alias=True)


def test_recipe_out_fills_missing_settings_and_nutrition():
    """Old rows can lack a settings or nutrition row, but the saved type requires both."""
    recipe = RecipeOut.model_validate(
        {
            "id": uuid4(),
            "user_id": uuid4(),
            "household_id": uuid4(),
            "group_id": uuid4(),
            "name": "test",
            "slug": "test",
            "settings": None,
            "nutrition": None,
        }
    )

    assert recipe.settings == RecipeSettings()
    assert recipe.nutrition == Nutrition()
