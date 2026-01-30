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
