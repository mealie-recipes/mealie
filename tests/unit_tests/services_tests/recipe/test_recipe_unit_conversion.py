import pytest

from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientUnit,
    RecipeIngredient,
    StandardizedUnitType,
)
from mealie.schema.recipe.unit_system import UnitSystem
from mealie.services.recipe.recipe_unit_conversion import RecipeUnitConverter


def _ingredient(quantity: float, standard_unit: StandardizedUnitType, standard_quantity: float) -> RecipeIngredient:
    return RecipeIngredient(
        quantity=quantity,
        unit=CreateIngredientUnit(
            name=standard_unit.value,
            standard_unit=standard_unit.value,
            standard_quantity=standard_quantity,
        ),
    )


@pytest.fixture
def converter() -> RecipeUnitConverter:
    return RecipeUnitConverter()


# --- Mass thresholds ---------------------------------------------------------


def test_grams_below_1000_stay_as_g(converter):
    ing = _ingredient(quantity=500, standard_unit=StandardizedUnitType.GRAM, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out.unit.abbreviation == "g"
    assert out.quantity == pytest.approx(500)


def test_grams_at_or_above_1000_round_to_kg(converter):
    ing = _ingredient(quantity=1500, standard_unit=StandardizedUnitType.GRAM, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out.unit.abbreviation == "kg"
    assert out.quantity == pytest.approx(1.5)


def test_oz_to_lb_when_at_least_1lb(converter):
    ing = _ingredient(quantity=20, standard_unit=StandardizedUnitType.OUNCE, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.US)
    assert out.unit.abbreviation == "lb"
    assert out.quantity == pytest.approx(1.25, rel=1e-2)


def test_metric_mass_below_1g_uses_mg(converter):
    ing = _ingredient(quantity=0.5, standard_unit=StandardizedUnitType.GRAM, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out.unit.abbreviation == "mg"
    assert out.quantity == pytest.approx(500)


# --- Volume thresholds -------------------------------------------------------


def test_us_cups_to_metric_volume(converter):
    ing = _ingredient(quantity=2, standard_unit=StandardizedUnitType.CUP, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    # Pint's `cup` is 1/16 US gallon = 236.59 ml, so 2 cups → 473.18 ml.
    assert out.unit.abbreviation == "ml"
    assert out.quantity == pytest.approx(473.18, rel=1e-3)


def test_us_cups_at_or_above_1l_use_l(converter):
    ing = _ingredient(quantity=5, standard_unit=StandardizedUnitType.CUP, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    # 5 cups × 236.59 ml ≈ 1182.94 ml = 1.183 l
    assert out.unit.abbreviation == "l"
    assert out.quantity == pytest.approx(1.183, rel=1e-2)


def test_imperial_pint_uses_568ml(converter):
    """Guard against Pint's US-default trap — imperial pint is 568.26 ml, not 473 ml."""
    ing = _ingredient(quantity=1000, standard_unit=StandardizedUnitType.MILLILITER, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.IMPERIAL)
    assert out.unit.name == "pint"
    # 1000 ml / 568.26125 ≈ 1.7598
    assert out.quantity == pytest.approx(1.76, rel=1e-2)


def test_imperial_volume_skips_imperial_cup_in_favor_of_ml(converter):
    """At 250 ml the US picker would emit cup; imperial deliberately uses ml instead."""
    ing = _ingredient(quantity=250, standard_unit=StandardizedUnitType.MILLILITER, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.IMPERIAL)
    assert out.unit.abbreviation == "ml"
    assert out.quantity == pytest.approx(250)


def test_imperial_small_volumes_render_in_ml(converter):
    """Pint has no imperial_tablespoon/imperial_teaspoon, and UK home cooks use ml below a pint."""
    ing = _ingredient(quantity=15, standard_unit=StandardizedUnitType.MILLILITER, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.IMPERIAL)
    assert out.unit.abbreviation == "ml"
    assert out.quantity == pytest.approx(15)


def test_pint_default_registry_returns_us_cup_for_us_target(converter):
    """Pint's default `cup` is 236.59 ml. 240 ml → just over 1 cup."""
    ing = _ingredient(quantity=240, standard_unit=StandardizedUnitType.MILLILITER, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.US)
    assert out.unit.abbreviation == "c"
    # 240 / 236.59 ≈ 1.0144
    assert out.quantity == pytest.approx(1.014, rel=1e-2)


# --- Skip / passthrough ------------------------------------------------------


def test_skip_when_unit_missing(converter):
    ing = RecipeIngredient(quantity=1, unit=None, note="a pinch")
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out is ing


def test_skip_when_standard_unit_null(converter):
    ing = RecipeIngredient(
        quantity=1,
        unit=CreateIngredientUnit(name="dash", standard_unit=None, standard_quantity=None),
    )
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out is ing


def test_skip_when_standard_unit_not_in_enum(converter):
    """A unit whose standard_unit is something Pint knows but isn't in StandardizedUnitType."""
    ing = RecipeIngredient(
        quantity=1,
        unit=CreateIngredientUnit(
            name="weird",
            standard_unit="furlong",
            standard_quantity=1,
        ),
    )
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    # Returns the original ingredient unchanged because StandardizedUnitType("furlong") raises ValueError.
    assert out is ing


def test_target_original_returns_input_unchanged(converter):
    ing = _ingredient(quantity=2, standard_unit=StandardizedUnitType.CUP, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.ORIGINAL)
    assert out is ing


def test_zero_quantity_handled(converter):
    ing = _ingredient(quantity=0, standard_unit=StandardizedUnitType.GRAM, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out.quantity == pytest.approx(0)


# --- Synthetic IngredientUnit fraction flag ----------------------------------


def test_synthetic_unit_fraction_flag_metric_is_false(converter):
    ing = _ingredient(quantity=1500, standard_unit=StandardizedUnitType.GRAM, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], UnitSystem.METRIC)
    assert out.unit.fraction is False


def test_synthetic_unit_fraction_flag_us_imperial_is_true(converter):
    ing_us = _ingredient(quantity=2, standard_unit=StandardizedUnitType.CUP, standard_quantity=1)
    [out_us] = converter.convert_ingredients([ing_us], UnitSystem.US)
    # cup → cup is a no-op conversion but still returns a synthetic unit with fraction=True.
    assert out_us.unit.fraction is True

    ing_metric = _ingredient(quantity=400, standard_unit=StandardizedUnitType.GRAM, standard_quantity=1)
    [out_imp] = converter.convert_ingredients([ing_metric], UnitSystem.IMPERIAL)
    assert out_imp.unit.fraction is True


# --- Parametrised matrix -----------------------------------------------------


@pytest.mark.parametrize("canonical", list(StandardizedUnitType))
@pytest.mark.parametrize("system", [UnitSystem.METRIC, UnitSystem.IMPERIAL, UnitSystem.US])
def test_every_canonical_x_target_pair_round_trips(converter, canonical, system):
    """Every (canonical, target) pair must produce a non-None quantity and unit."""
    ing = _ingredient(quantity=1, standard_unit=canonical, standard_quantity=1)
    [out] = converter.convert_ingredients([ing], system)
    assert out.quantity is not None
    assert out.unit is not None
