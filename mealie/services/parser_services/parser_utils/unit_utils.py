from typing import Literal, overload

from pint import Quantity, Unit, UnitRegistry


class UnitNotFound(Exception):
    """Raised when trying to access a unit not found in the unit registry"""

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
                raise UnitNotFound() from e
            return unit

    def can_convert(self, unit: str | Unit, to_unit: str | Unit) -> bool:
        """Whether or not a given unit can be converted into another unit"""

        unit = self.parse(unit)
        to_unit = self.parse(to_unit)

        if not (isinstance(unit, Unit) and isinstance(to_unit, Unit)):
            return False

        unit, to_unit = self._resolve_ounce(unit, to_unit)
        return unit.is_compatible_with(to_unit)

    def convert(self, quantity: float, unit: str | Unit, to_unit: str | Unit) -> tuple[float, Unit]:
        """
        Convert a quantity and a unit into another unit

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

        # Choose which unit to keep
        # If the result is >= 1, prefer the larger one, otherwise prefer the smaller one
        if unit_1 > unit_2:
            larger, smaller = unit_1, unit_2
        else:
            larger, smaller = unit_2, unit_1

        if abs(out.magnitude) >= 1:
            out = out.to(larger)
        else:
            out = out.to(smaller)

        return float(out.magnitude), out.units
