from uuid import uuid4

import pytest

from mealie.schema.recipe.recipe_ingredient import (
    IngredientFood,
    IngredientUnit,
    RecipeIngredient,
)


@pytest.mark.parametrize(
    ["quantity", "quantity_display_decimal", "quantity_display_fraction", "expect_plural_unit", "expect_plural_food"],
    [
        [0, "", "", False, True],
        [0.5, "0.5", "¹/₂", False, False],
        [1, "1", "1", False, False],
        [1.5, "1.5", "1 ¹/₂", True, True],
        [2, "2", "2", True, True],
    ],
)
@pytest.mark.parametrize(
    ["unit", "expect_display_fraction", "expected_unit_singular_string", "expected_unit_plural_string"],
    [
        [
            None,
            True,
            "",
            "",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name=None,
                abbreviation="tbsp",
                plural_abbreviation=None,
                use_abbreviation=False,
                fraction=True,
            ),
            True,
            "tablespoon",
            "tablespoon",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name=None,
                abbreviation="tbsp",
                plural_abbreviation=None,
                use_abbreviation=False,
                fraction=False,
            ),
            False,
            "tablespoon",
            "tablespoon",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name=None,
                abbreviation="tbsp",
                plural_abbreviation=None,
                use_abbreviation=True,
                fraction=True,
            ),
            True,
            "tbsp",
            "tbsp",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name=None,
                abbreviation="tbsp",
                plural_abbreviation=None,
                use_abbreviation=True,
                fraction=False,
            ),
            False,
            "tbsp",
            "tbsp",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name="tablespoons",
                abbreviation="tbsp",
                plural_abbreviation="tbsps",
                use_abbreviation=False,
                fraction=True,
            ),
            True,
            "tablespoon",
            "tablespoons",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name="tablespoons",
                abbreviation="tbsp",
                plural_abbreviation="tbsps",
                use_abbreviation=False,
                fraction=False,
            ),
            False,
            "tablespoon",
            "tablespoons",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name="tablespoons",
                abbreviation="tbsp",
                plural_abbreviation="tbsps",
                use_abbreviation=True,
                fraction=True,
            ),
            True,
            "tbsp",
            "tbsps",
        ],
        [
            IngredientUnit(
                id=uuid4(),
                name="tablespoon",
                plural_name="tablespoons",
                abbreviation="tbsp",
                plural_abbreviation="tbsps",
                use_abbreviation=True,
                fraction=False,
            ),
            False,
            "tbsp",
            "tbsps",
        ],
    ],
)
@pytest.mark.parametrize(
    ["food", "expected_food_singular_string", "expected_food_plural_string"],
    [
        [
            IngredientFood(id=uuid4(), name="chopped onion", plural_name=None),
            "chopped onion",
            "chopped onion",
        ],
        [
            IngredientFood(id=uuid4(), name="chopped onion", plural_name="chopped onions"),
            "chopped onion",
            "chopped onions",
        ],
    ],
)
@pytest.mark.parametrize("note", ["very thin", ""])
@pytest.mark.parametrize("use_food", [True, False])
def test_ingredient_display(
    quantity: float | None,
    quantity_display_decimal: str,
    quantity_display_fraction: str,
    unit: IngredientUnit | None,
    food: IngredientFood,
    note: str,
    use_food: bool,
    expect_display_fraction: bool,
    expect_plural_unit: bool,
    expect_plural_food: bool,
    expected_unit_singular_string: str,
    expected_unit_plural_string: str,
    expected_food_singular_string: str,
    expected_food_plural_string: str,
):
    expected_components = []
    if use_food:
        if expect_display_fraction:
            expected_components.append(quantity_display_fraction)
        else:
            expected_components.append(quantity_display_decimal)

        if quantity:
            if expect_plural_unit:
                expected_components.append(expected_unit_plural_string)
            else:
                expected_components.append(expected_unit_singular_string)

        if expect_plural_food:
            expected_components.append(expected_food_plural_string)
        else:
            expected_components.append(expected_food_singular_string)

        expected_components.append(note)

    else:
        if quantity != 0 and quantity != 1:
            if expect_display_fraction:
                expected_components.append(quantity_display_fraction)
            else:
                expected_components.append(quantity_display_decimal)

        expected_components.append(note)

    expected_display_value = " ".join(c for c in expected_components if c)
    ingredient = RecipeIngredient(
        quantity=quantity, unit=unit, food=food, note=note, use_food=use_food, disable_amount=not use_food
    )
    assert ingredient.display == expected_display_value
