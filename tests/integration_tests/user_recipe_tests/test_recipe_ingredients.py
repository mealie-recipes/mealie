from unittest.mock import MagicMock
from uuid import uuid4

import pytest
from pytest import MonkeyPatch

from mealie.lang.locale_config import LocalePluralFoodHandling
from mealie.schema.recipe.recipe_ingredient import (
    IngredientFood,
    IngredientUnit,
    RecipeIngredient,
)


@pytest.mark.parametrize(
    ["quantity", "quantity_display_decimal", "quantity_display_fraction", "expect_plural_unit"],
    [
        [0, "", "", False],
        [0.5, "0.5", "¹/₂", False],
        [1, "1", "1", False],
        [1.5, "1.5", "1 ¹/₂", True],
        [2, "2", "2", True],
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
            None,
            "",
            "",
        ],
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
@pytest.mark.parametrize("note", ["very thin", "", None])
@pytest.mark.parametrize(
    "plural_handling",
    [
        LocalePluralFoodHandling.ALWAYS,
        LocalePluralFoodHandling.NEVER,
        LocalePluralFoodHandling.WITHOUT_UNIT,
    ],
)
def test_ingredient_display(
    quantity: float | None,
    quantity_display_decimal: str,
    quantity_display_fraction: str,
    unit: IngredientUnit | None,
    food: IngredientFood | None,
    note: str | None,
    expect_display_fraction: bool,
    expect_plural_unit: bool,
    expected_unit_singular_string: str,
    expected_unit_plural_string: str,
    expected_food_singular_string: str,
    expected_food_plural_string: str,
    plural_handling: LocalePluralFoodHandling,
    monkeypatch: MonkeyPatch,
):

    mock_locale_cfg = MagicMock()
    mock_locale_cfg.plural_food_handling = plural_handling
    monkeypatch.setattr("mealie.schema.recipe.recipe_ingredient.get_locale_context", lambda: ("en-US", mock_locale_cfg))

    # Calculate expect_plural_food based on plural_handling strategy
    if quantity and quantity <= 1:
        expect_plural_food = False
    else:
        match plural_handling:
            case LocalePluralFoodHandling.NEVER:
                expect_plural_food = False
            case LocalePluralFoodHandling.WITHOUT_UNIT:
                expect_plural_food = not (quantity and unit)
            case LocalePluralFoodHandling.ALWAYS:
                expect_plural_food = True
            case _:
                expect_plural_food = False

    expected_components = []
    if expect_display_fraction:
        expected_components.append(quantity_display_fraction)
    else:
        expected_components.append(quantity_display_decimal)

    if quantity:
        if expect_plural_unit:
            expected_components.append(expected_unit_plural_string)
        else:
            expected_components.append(expected_unit_singular_string)

    if food:
        if expect_plural_food:
            expected_components.append(expected_food_plural_string)
        else:
            expected_components.append(expected_food_singular_string)

    expected_components.append(note or "")

    expected_display_value = " ".join(c for c in expected_components if c)
    ingredient = RecipeIngredient(quantity=quantity, unit=unit, food=food, note=note)
    assert ingredient.display == expected_display_value
