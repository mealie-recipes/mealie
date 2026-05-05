from enum import StrEnum


class UnitSystem(StrEnum):
    """
    Target unit system for displaying recipe ingredients and instruction temperatures.

    `original` is the no-op: display values exactly as authored.
    `metric` uses g/kg/ml/l and Celsius.
    `imperial` uses UK imperial volumes (skipping `imperial_cup` to avoid Pint's
    284 ml definition mismatching common 250 ml usage) and Celsius.
    `us` uses US customary volumes and Fahrenheit.
    """

    ORIGINAL = "original"
    METRIC = "metric"
    IMPERIAL = "imperial"
    US = "us"
