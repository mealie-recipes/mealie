from typing import TYPE_CHECKING, Literal, overload

from pint import Quantity, Unit, UnitRegistry

if TYPE_CHECKING:
    from mealie.schema.recipe.recipe_ingredient import CreateIngredientUnit


class UnitNotFound(Exception):
    """Raised when trying to access a unit not found in the unit registry."""

    def __init__(self, message: str = "Unit not found in unit registry"):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"


class UnitConverter:
    def __init__(self):
        self.ureg = UnitRegistry()

    def _resolve_ounce(self, unit_1: Unit, unit_2: Unit) -> tuple[Unit, Unit]:
        """
        Often times "ounce" is used in place of "fluid ounce" in recipes.
        When trying to convert/combine ounces with a volume, we can assume it should have been a fluid ounce.
        This function will convert ounces to fluid ounces if the other unit is a volume.
        """

        OUNCE = self.ureg("ounce")
        FL_OUNCE = self.ureg("fluid_ounce")
        VOLUME = "[length] ** 3"

        if unit_1 == OUNCE and unit_2.dimensionality == VOLUME:
            return FL_OUNCE, unit_2
        if unit_2 == OUNCE and unit_1.dimensionality == VOLUME:
            return unit_1, FL_OUNCE

        return unit_1, unit_2

    @overload
    def parse(self, unit: str | Unit, strict: Literal[False] = False) -> str | Unit: ...

    @overload
    def parse(self, unit: str | Unit, strict: Literal[True]) -> Unit: ...

    def parse(self, unit: str | Unit, strict: bool = False) -> str | Unit:
        """
        Parse a string unit into a pint.Unit.

        If strict is False (default), returns a pint.Unit if it exists, otherwise returns the original string.
        If strict is True, raises UnitNotFound instead of returning a string.
        If the input is already a parsed pint.Unit, returns it as-is.
        """
        if isinstance(unit, Unit):
            return unit

        try:
            return self.ureg(unit).units
        except Exception as e:
            if strict:
                raise UnitNotFound(f"Unit '{unit}' not found in unit registry") from e
            return unit

    def can_convert(self, unit: str | Unit, to_unit: str | Unit) -> bool:
        """Whether or not a given unit can be converted into another unit."""

        unit = self.parse(unit)
        to_unit = self.parse(to_unit)

        if not (isinstance(unit, Unit) and isinstance(to_unit, Unit)):
            return False

        unit, to_unit = self._resolve_ounce(unit, to_unit)
        return unit.is_compatible_with(to_unit)

    def convert(self, quantity: float, unit: str | Unit, to_unit: str | Unit) -> tuple[float, Unit]:
        """
        Convert a quantity and a unit into another unit.

        Returns tuple[quantity, unit]
        """

        unit = self.parse(unit, strict=True)
        to_unit = self.parse(to_unit, strict=True)
        unit, to_unit = self._resolve_ounce(unit, to_unit)

        qty = quantity * unit
        converted = qty.to(to_unit)
        return float(converted.magnitude), converted.units

    def merge(self, quantity_1: float, unit_1: str | Unit, quantity_2: float, unit_2: str | Unit) -> tuple[float, Unit]:
        """Merge two quantities together"""

        unit_1 = self.parse(unit_1, strict=True)
        unit_2 = self.parse(unit_2, strict=True)
        unit_1, unit_2 = self._resolve_ounce(unit_1, unit_2)

        q1 = quantity_1 * unit_1
        q2 = quantity_2 * unit_2

        out: Quantity = q1 + q2
        return float(out.magnitude), out.units


def merge_quantity_and_unit[T: CreateIngredientUnit](
    qty_1: float, unit_1: T, qty_2: float, unit_2: T
) -> tuple[float, T]:
    """
    Merge a quantity and unit.

    Returns tuple[quantity, unit]
    """

    if not (unit_1.standard_quantity and unit_1.standard_unit and unit_2.standard_quantity and unit_2.standard_unit):
        raise ValueError("Both units must contain standardized unit data")

    PINT_UNIT_1_TXT = "_mealie_unit_1"
    PINT_UNIT_2_TXT = "_mealie_unit_2"

    uc = UnitConverter()

    # pre-process units to account for ounce -> fluid_ounce conversion
    unit_1_standard = uc.parse(unit_1.standard_unit, strict=True)
    unit_2_standard = uc.parse(unit_2.standard_unit, strict=True)
    unit_1_standard, unit_2_standard = uc._resolve_ounce(unit_1_standard, unit_2_standard)

    # create custon unit definition so pint can handle them natively
    uc.ureg.define(f"{PINT_UNIT_1_TXT} = {unit_1.standard_quantity} * {unit_1_standard}")
    uc.ureg.define(f"{PINT_UNIT_2_TXT} = {unit_2.standard_quantity} * {unit_2_standard}")

    pint_unit_1 = uc.parse(PINT_UNIT_1_TXT)
    pint_unit_2 = uc.parse(PINT_UNIT_2_TXT)

    merged_q, merged_u = uc.merge(qty_1, pint_unit_1, qty_2, pint_unit_2)

    # Convert to the bigger unit if quantity >= 1, else the smaller unit
    merged_q, merged_u = uc.convert(merged_q, merged_u, max(pint_unit_1, pint_unit_2))
    if abs(merged_q) < 1:
        merged_q, merged_u = uc.convert(merged_q, merged_u, min(pint_unit_1, pint_unit_2))

    if str(merged_u) == PINT_UNIT_1_TXT:
        return merged_q, unit_1
    else:
        return merged_q, unit_2
