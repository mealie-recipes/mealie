"""Convert temperatures embedded in recipe instruction text.

Scans for `<number>[-<number>] [°][F|C]` patterns and rewrites them in the
target system's preferred temperature unit (metric/imperial → Celsius,
us → Fahrenheit).
"""

import re

from mealie.schema.recipe.unit_system import UnitSystem

# Match a single number or a number range, optionally followed by a degree sign,
# then F or C with a non-letter trailing boundary (so "vitamin C" or "350Free"
# don't match).
_TEMP_RE = re.compile(
    r"(?P<lo>\d+(?:\.\d+)?)"
    r"(?:\s*[-–—]\s*(?P<hi>\d+(?:\.\d+)?))?"
    r"\s*°?\s*(?P<unit>[FCfc])(?![A-Za-z])"
)


def convert_instruction_temperatures(text: str | None, target: UnitSystem) -> str | None:
    """Rewrite F↔C temperatures in `text` to match the target system.

    Returns `text` unchanged for None / empty input or `target == ORIGINAL`.
    metric and imperial both render Celsius (UK kitchens use °C). us renders Fahrenheit.
    """
    if not text or target == UnitSystem.ORIGINAL:
        return text

    target_unit = "F" if target == UnitSystem.US else "C"

    def replace(match: re.Match[str]) -> str:
        source_unit = match.group("unit").upper()
        if source_unit == target_unit:
            return match.group(0)

        lo_text = match.group("lo")
        hi_text = match.group("hi")
        lo_converted = _convert_value(lo_text, source_unit, target_unit)

        if hi_text is not None:
            hi_converted = _convert_value(hi_text, source_unit, target_unit)
            return f"{lo_converted}-{hi_converted}°{target_unit}"

        return f"{lo_converted}°{target_unit}"

    return _TEMP_RE.sub(replace, text)


def _convert_value(value_text: str, source: str, target: str) -> str:
    value = float(value_text)
    if source == "F" and target == "C":
        converted = (value - 32.0) * 5.0 / 9.0
    elif source == "C" and target == "F":
        converted = value * 9.0 / 5.0 + 32.0
    else:
        converted = value

    # Preserve "looks integer" inputs as integers; otherwise keep one decimal.
    if "." not in value_text:
        return str(round(converted))
    return f"{round(converted, 1):g}"
