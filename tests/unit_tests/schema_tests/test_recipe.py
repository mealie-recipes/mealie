from typing import Any
from uuid import uuid4

import pytest

from mealie.schema.recipe import RecipeSummary

SHOULD_ERROR = "this_test_should_error"


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
        recipe = RecipeSummary(
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


@pytest.mark.parametrize("field", ["recipe_yield", "total_time", "prep_time", "cook_time", "perform_time"])
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
    recipe = RecipeSummary(
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
        recipe_yield_quantity=recipe_yield_quantity,
        recipe_yield=recipe_yield,
        recipe_servings=recipe_servings,
    )

    assert recipe.recipe_yield_display == expected


def test_recipe_preserves_existing_slug():
    recipe = RecipeSummary(
        id=uuid4(),
        user_id=uuid4(),
        household_id=uuid4(),
        group_id=uuid4(),
        name="Bols nourrissants (copie de Zuppa)",
        slug="nourish-bowls-zuppa-copycat",
    )

    assert recipe.slug == "nourish-bowls-zuppa-copycat"
