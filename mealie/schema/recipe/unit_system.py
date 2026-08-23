from enum import StrEnum


class UnitSystem(StrEnum):
    """
    Target unit system for displaying recipe ingredient quantities.

    `original` is the no-op: display values exactly as authored.
    `metric` uses mg/g/kg and ml/l.
    `imperial` uses UK imperial volumes and shares mass units with `us`
    (the avoirdupois ounce and pound are identical in both systems).
    `us` uses US customary volumes (tsp/tbsp/cup/pint).

    Conversion is display-only and never crosses dimensions: mass stays mass and
    volume stays volume. Converting cups to grams needs a per-food density, which
    Mealie does not store.
    """

    ORIGINAL = "original"
    METRIC = "metric"
    IMPERIAL = "imperial"
    US = "us"


class TemperatureUnit(StrEnum):
    """
    Target unit for temperatures found in recipe instruction text.

    `system` derives the unit from the chosen `UnitSystem` (metric and imperial
    render Celsius, us renders Fahrenheit, original leaves text untouched). It is
    a separate setting because the two preferences genuinely come apart: cooks who
    measure in grams but own a Fahrenheit oven are common.
    """

    SYSTEM = "system"
    CELSIUS = "celsius"
    FAHRENHEIT = "fahrenheit"
