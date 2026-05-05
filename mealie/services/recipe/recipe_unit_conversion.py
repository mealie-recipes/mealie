"""Recipe ingredient unit conversion for display.

Converts a recipe's ingredients into the user's preferred unit system on the fly.
The DB stores the authored values verbatim — this service produces a converted
view without writing anything back.
"""

from collections.abc import Iterable
from copy import deepcopy
from dataclasses import dataclass

from pint.errors import DimensionalityError, UndefinedUnitError

from mealie.core.root_logger import get_logger
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientUnit,
    RecipeIngredient,
    StandardizedUnitType,
)
from mealie.schema.recipe.unit_system import UnitSystem
from mealie.services.parser_services.parser_utils.unit_utils import UnitConverter

logger = get_logger()


@dataclass(frozen=True)
class _DisplayUnit:
    """Static metadata for a unit chosen by the picker."""

    pint_id: str
    name: str
    plural_name: str
    abbreviation: str
    plural_abbreviation: str
    fraction: bool


# Decimal display for metric units; fractional display for US/imperial customary units.
# `pint_id` is the identifier passed to UnitConverter (must exist in the Pint registry).
DISPLAY_UNITS: dict[str, _DisplayUnit] = {
    "milligram": _DisplayUnit("milligram", "milligram", "milligrams", "mg", "mg", fraction=False),
    "gram": _DisplayUnit("gram", "gram", "grams", "g", "g", fraction=False),
    "kilogram": _DisplayUnit("kilogram", "kilogram", "kilograms", "kg", "kg", fraction=False),
    "milliliter": _DisplayUnit("milliliter", "milliliter", "milliliters", "ml", "ml", fraction=False),
    "liter": _DisplayUnit("liter", "liter", "liters", "l", "l", fraction=False),
    "ounce": _DisplayUnit("ounce", "ounce", "ounces", "oz", "oz", fraction=True),
    "pound": _DisplayUnit("pound", "pound", "pounds", "lb", "lbs", fraction=True),
    # US customary volumes — Pint defaults to these
    "teaspoon": _DisplayUnit("teaspoon", "teaspoon", "teaspoons", "tsp", "tsp", fraction=True),
    "tablespoon": _DisplayUnit("tablespoon", "tablespoon", "tablespoons", "tbsp", "tbsp", fraction=True),
    "cup": _DisplayUnit("cup", "cup", "cups", "c", "c", fraction=True),
    "pint": _DisplayUnit("pint", "pint", "pints", "pt", "pt", fraction=True),
    # UK imperial pint (568.26 ml). `imperial_cup` is intentionally omitted:
    # Pint defines it as 284 ml (half an imperial pint), but UK/AU recipes
    # commonly use 250 ml. Pint also has no `imperial_tablespoon`/`imperial_teaspoon`,
    # and UK home cooks generally use ml/g for volumes below an imperial pint.
    "imperial_pint": _DisplayUnit("imperial_pint", "pint", "pints", "pt", "pt", fraction=True),
}


class RecipeUnitConverter:
    """Service that produces a display-time conversion of recipe ingredients.

    Construct once per request and reuse `convert_ingredients` to avoid
    re-instantiating the underlying Pint registry.
    """

    def __init__(self) -> None:
        self._uc = UnitConverter()

    def convert_ingredients(
        self, ingredients: Iterable[RecipeIngredient], target: UnitSystem
    ) -> list[RecipeIngredient]:
        return [self._convert_one(ing, target) for ing in ingredients]

    def _convert_one(self, ingredient: RecipeIngredient, target: UnitSystem) -> RecipeIngredient:
        if target == UnitSystem.ORIGINAL:
            return ingredient

        canonical = self._canonical(ingredient)
        if canonical is None:
            return ingredient

        magnitude, canonical_unit = canonical

        display = self._pick_display_unit(canonical_unit, target, magnitude)
        if display is None:
            return ingredient

        try:
            converted_qty, _ = self._uc.convert(magnitude, canonical_unit.value, display.pint_id)
        except (DimensionalityError, UndefinedUnitError, Exception) as e:
            logger.warning(
                "Could not convert %s %s to %s: %s",
                magnitude,
                canonical_unit,
                display.pint_id,
                e,
            )
            return ingredient

        new_ing = deepcopy(ingredient)
        new_ing.quantity = converted_qty
        new_ing.unit = CreateIngredientUnit(
            name=display.name,
            plural_name=display.plural_name,
            abbreviation=display.abbreviation,
            plural_abbreviation=display.plural_abbreviation,
            fraction=display.fraction,
            use_abbreviation=True,
        )
        # The original cached display string is now stale; clear it so format_display() re-runs.
        new_ing.display = ""
        return new_ing

    @staticmethod
    def _canonical(ingredient: RecipeIngredient) -> tuple[float, StandardizedUnitType] | None:
        unit = ingredient.unit
        if unit is None:
            return None
        if not unit.standard_unit or unit.standard_quantity is None:
            return None
        try:
            canonical_type = StandardizedUnitType(unit.standard_unit)
        except ValueError:
            return None

        quantity = ingredient.quantity or 0.0
        return quantity * unit.standard_quantity, canonical_type

    @staticmethod
    def _pick_display_unit(
        canonical_unit: StandardizedUnitType,
        target: UnitSystem,
        magnitude: float,
    ) -> _DisplayUnit | None:
        magnitude_abs = abs(magnitude)

        if canonical_unit in _MASS_CANONICALS:
            magnitude_g = _to_grams(canonical_unit, magnitude_abs)
            return _pick_mass(magnitude_g, target)

        if canonical_unit in _VOLUME_CANONICALS:
            magnitude_ml = _to_milliliters(canonical_unit, magnitude_abs)
            return _pick_volume(magnitude_ml, target)

        return None


_MASS_CANONICALS = {
    StandardizedUnitType.GRAM,
    StandardizedUnitType.KILOGRAM,
    StandardizedUnitType.OUNCE,
    StandardizedUnitType.POUND,
}
_VOLUME_CANONICALS = {
    StandardizedUnitType.MILLILITER,
    StandardizedUnitType.LITER,
    StandardizedUnitType.FLUID_OUNCE,
    StandardizedUnitType.CUP,
}


def _to_grams(canonical: StandardizedUnitType, magnitude: float) -> float:
    if canonical == StandardizedUnitType.GRAM:
        return magnitude
    if canonical == StandardizedUnitType.KILOGRAM:
        return magnitude * 1000.0
    if canonical == StandardizedUnitType.OUNCE:
        return magnitude * 28.349523125
    if canonical == StandardizedUnitType.POUND:
        return magnitude * 453.59237
    raise ValueError(f"Not a mass canonical: {canonical}")


def _to_milliliters(canonical: StandardizedUnitType, magnitude: float) -> float:
    if canonical == StandardizedUnitType.MILLILITER:
        return magnitude
    if canonical == StandardizedUnitType.LITER:
        return magnitude * 1000.0
    if canonical == StandardizedUnitType.FLUID_OUNCE:
        # Pint's default fluid_ounce is US-customary: 29.5735 ml.
        return magnitude * 29.5735295625
    if canonical == StandardizedUnitType.CUP:
        # Pint's default cup is 1/16 US gallon = 236.59 ml (NOT the FDA legal 240 ml).
        return magnitude * 236.5882365
    raise ValueError(f"Not a volume canonical: {canonical}")


def _pick_mass(magnitude_g: float, target: UnitSystem) -> _DisplayUnit:
    if target == UnitSystem.METRIC:
        if magnitude_g >= 1000.0:
            return DISPLAY_UNITS["kilogram"]
        if magnitude_g < 1.0 and magnitude_g > 0:
            return DISPLAY_UNITS["milligram"]
        return DISPLAY_UNITS["gram"]
    # imperial and us share mass units (UK and US ounces are equal for mass).
    if magnitude_g >= 453.59237:
        return DISPLAY_UNITS["pound"]
    return DISPLAY_UNITS["ounce"]


def _pick_volume(magnitude_ml: float, target: UnitSystem) -> _DisplayUnit:
    if target == UnitSystem.METRIC:
        if magnitude_ml >= 1000.0:
            return DISPLAY_UNITS["liter"]
        return DISPLAY_UNITS["milliliter"]
    if target == UnitSystem.IMPERIAL:
        # Imperial volumes use imperial_pint above 568 ml and ml below.
        # imperial_cup is skipped (Pint = 284 ml, but UK/AU commonly use 250 ml).
        # imperial_tablespoon/imperial_teaspoon don't exist in Pint, and UK
        # home cooks usually express small volumes in ml anyway.
        if magnitude_ml >= 568.26125:
            return DISPLAY_UNITS["imperial_pint"]
        return DISPLAY_UNITS["milliliter"]
    # US customary (Pint's defaults: cup = 236.59 ml, pint = 473.18 ml, tbsp = 14.79 ml)
    if magnitude_ml >= 473.176473:
        return DISPLAY_UNITS["pint"]
    if magnitude_ml >= 236.5882365:
        return DISPLAY_UNITS["cup"]
    if magnitude_ml >= 14.7867647:
        return DISPLAY_UNITS["tablespoon"]
    return DISPLAY_UNITS["teaspoon"]
