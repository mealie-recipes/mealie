"""Recipe ingredient unit conversion for display.

Converts a recipe's ingredients into the user's preferred unit system on the fly.
The DB stores the authored values verbatim — this service produces a converted
view without writing anything back.

Imperial volumes intentionally skip `imperial_cup` (Pint defines it as 284 ml,
but UK/AU recipes commonly use 250 ml) and Pint has no `imperial_tablespoon`/
`imperial_teaspoon`; UK home cooks typically render small volumes in ml.
"""

from collections.abc import Iterable
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

# Module-level Pint registry singleton. `pint.UnitRegistry()` is expensive to
# initialise (~50–200 ms parsing the default unit definitions); reusing one
# instance across requests turns the conversion endpoint into a fast path.
# Safe because RecipeUnitConverter only reads from the registry — it never
# calls `define()` on it (unlike `merge_quantity_and_unit`, which uses its
# own short-lived registry).
_SHARED_UC = UnitConverter()


@dataclass(frozen=True)
class _DisplayUnit:
    """Static metadata for a unit chosen by the picker."""

    pint_id: str
    name: str
    plural_name: str
    abbreviation: str
    plural_abbreviation: str
    fraction: bool


_MILLIGRAM = _DisplayUnit("milligram", "milligram", "milligrams", "mg", "mg", fraction=False)
_GRAM = _DisplayUnit("gram", "gram", "grams", "g", "g", fraction=False)
_KILOGRAM = _DisplayUnit("kilogram", "kilogram", "kilograms", "kg", "kg", fraction=False)
_MILLILITER = _DisplayUnit("milliliter", "milliliter", "milliliters", "ml", "ml", fraction=False)
_LITER = _DisplayUnit("liter", "liter", "liters", "l", "l", fraction=False)
_OUNCE = _DisplayUnit("ounce", "ounce", "ounces", "oz", "oz", fraction=True)
_POUND = _DisplayUnit("pound", "pound", "pounds", "lb", "lbs", fraction=True)
_TEASPOON = _DisplayUnit("teaspoon", "teaspoon", "teaspoons", "tsp", "tsp", fraction=True)
_TABLESPOON = _DisplayUnit("tablespoon", "tablespoon", "tablespoons", "tbsp", "tbsp", fraction=True)
_CUP = _DisplayUnit("cup", "cup", "cups", "c", "c", fraction=True)
_PINT = _DisplayUnit("pint", "pint", "pints", "pt", "pt", fraction=True)
_IMPERIAL_PINT = _DisplayUnit("imperial_pint", "pint", "pints", "pt", "pt", fraction=True)


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


class RecipeUnitConverter:
    """Service that produces a display-time conversion of recipe ingredients."""

    def __init__(self) -> None:
        self._uc = _SHARED_UC

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
        except (DimensionalityError, UndefinedUnitError) as e:
            logger.warning(
                "Could not convert %s %s to %s: %s",
                magnitude,
                canonical_unit,
                display.pint_id,
                e,
            )
            return ingredient

        new_ing = ingredient.model_copy(deep=True)
        new_ing.quantity = converted_qty
        new_ing.unit = CreateIngredientUnit(
            name=display.name,
            plural_name=display.plural_name,
            abbreviation=display.abbreviation,
            plural_abbreviation=display.plural_abbreviation,
            fraction=display.fraction,
            use_abbreviation=True,
        )
        new_ing.display = new_ing._format_display()
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

    def _pick_display_unit(
        self,
        canonical_unit: StandardizedUnitType,
        target: UnitSystem,
        magnitude: float,
    ) -> _DisplayUnit | None:
        magnitude_abs = abs(magnitude)

        if canonical_unit in _MASS_CANONICALS:
            magnitude_g = self._to_base(canonical_unit, magnitude_abs, "gram")
            return _pick_mass(magnitude_g, target)

        if canonical_unit in _VOLUME_CANONICALS:
            magnitude_ml = self._to_base(canonical_unit, magnitude_abs, "milliliter")
            return _pick_volume(magnitude_ml, target)

        return None

    def _to_base(self, canonical: StandardizedUnitType, magnitude: float, base: str) -> float:
        if canonical.value == base:
            return magnitude
        magnitude_base, _ = self._uc.convert(magnitude, canonical.value, base)
        return magnitude_base


def _pick_mass(magnitude_g: float, target: UnitSystem) -> _DisplayUnit:
    if target == UnitSystem.METRIC:
        if magnitude_g >= 1000.0:
            return _KILOGRAM
        if 0 < magnitude_g < 1.0:
            return _MILLIGRAM
        return _GRAM
    # imperial and us share mass units (UK and US ounces are equal for mass).
    if magnitude_g >= 453.59237:
        return _POUND
    return _OUNCE


def _pick_volume(magnitude_ml: float, target: UnitSystem) -> _DisplayUnit:
    if target == UnitSystem.METRIC:
        if magnitude_ml >= 1000.0:
            return _LITER
        return _MILLILITER
    if target == UnitSystem.IMPERIAL:
        if magnitude_ml >= 568.26125:
            return _IMPERIAL_PINT
        return _MILLILITER
    # US customary (Pint's defaults: cup = 236.59 ml, pint = 473.18 ml, tbsp = 14.79 ml)
    if magnitude_ml >= 473.176473:
        return _PINT
    if magnitude_ml >= 236.5882365:
        return _CUP
    if magnitude_ml >= 14.7867647:
        return _TABLESPOON
    return _TEASPOON
