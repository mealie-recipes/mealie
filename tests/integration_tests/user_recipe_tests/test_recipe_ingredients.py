from uuid import uuid4

import pytest

from mealie.schema.group.group_preferences import GroupPreferencesPluralHandling
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
def test_ingredient_display(
    quantity: float | None,
    quantity_display_decimal: str,
    quantity_display_fraction: str,
    unit: IngredientUnit | None,
    food: IngredientFood | None,
    note: str | None,
    expect_display_fraction: bool,
    expect_plural_unit: bool,
    expect_plural_food: bool,
    expected_unit_singular_string: str,
    expected_unit_plural_string: str,
    expected_food_singular_string: str,
    expected_food_plural_string: str,
):
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
    ingredient = RecipeIngredient(
        quantity=quantity,
        unit=unit,
        food=food,
        note=note,
        plural_handling=GroupPreferencesPluralHandling.always_pluralize,
    )
    assert ingredient.display == expected_display_value


@pytest.mark.parametrize(
    ["quantity", "unit", "food", "result_map"],
    [
        [
            0,
            IngredientUnit(id=uuid4(), name="tbsp", plural_name="tbsps"),
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "onions",
                GroupPreferencesPluralHandling.always_pluralize: "onions",
            },
        ],
        [
            0,
            None,
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "onions",
                GroupPreferencesPluralHandling.always_pluralize: "onions",
            },
        ],
        [
            0.5,
            IngredientUnit(id=uuid4(), name="tbsp", plural_name="tbsps"),
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "¹/₂ tbsp onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "¹/₂ tbsp onion",
                GroupPreferencesPluralHandling.always_pluralize: "¹/₂ tbsp onion",
            },
        ],
        [
            0.5,
            None,
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "¹/₂ onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "¹/₂ onion",
                GroupPreferencesPluralHandling.always_pluralize: "¹/₂ onion",
            },
        ],
        [
            1,
            IngredientUnit(id=uuid4(), name="tbsp", plural_name="tbsps"),
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "1 tbsp onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "1 tbsp onion",
                GroupPreferencesPluralHandling.always_pluralize: "1 tbsp onion",
            },
        ],
        [
            1,
            None,
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "1 onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "1 onion",
                GroupPreferencesPluralHandling.always_pluralize: "1 onion",
            },
        ],
        [
            2,
            IngredientUnit(id=uuid4(), name="tbsp", plural_name="tbsps"),
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "2 tbsps onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "2 tbsps onion",
                GroupPreferencesPluralHandling.always_pluralize: "2 tbsps onions",
            },
        ],
        [
            2,
            None,
            IngredientFood(id=uuid4(), name="onion", plural_name="onions"),
            {
                GroupPreferencesPluralHandling.disable: "2 onion",
                GroupPreferencesPluralHandling.pluralize_food_without_unit: "2 onions",
                GroupPreferencesPluralHandling.always_pluralize: "2 onions",
            },
        ],
    ],
)
def test_ingredient_display_plural_handling(
    quantity: float,
    unit: IngredientUnit | None,
    food: IngredientFood,
    result_map: dict[GroupPreferencesPluralHandling, str],
):
    for plural_handling, expected_display in result_map.items():
        ingredient = RecipeIngredient(
            quantity=quantity,
            unit=unit,
            food=food,
            plural_handling=plural_handling,
        )

        try:
            assert ingredient.display == expected_display
        except AssertionError as e:
            unit_name = unit.name if unit else None
            food_name = food.name
            raise AssertionError(
                f"Failed for {quantity=}, {unit_name=}, {food_name=}, {plural_handling.value=}. "
                f"Expected '{expected_display}', got '{ingredient.display}'"
            ) from e
