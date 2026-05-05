import pytest

from mealie.schema.recipe.unit_system import UnitSystem
from mealie.services.recipe.recipe_temperature_conversion import convert_instruction_temperatures


def test_fahrenheit_to_celsius_integer_rounds():
    assert convert_instruction_temperatures("Bake at 350°F", UnitSystem.METRIC) == "Bake at 177°C"


def test_celsius_to_fahrenheit_with_decimal_keeps_one_dp():
    assert convert_instruction_temperatures("Cook at 175.5°C", UnitSystem.US) == "Cook at 347.9°F"


def test_range_350_to_375f_round_trip():
    out = convert_instruction_temperatures("Bake at 350-375°F for 30 minutes", UnitSystem.METRIC)
    assert out == "Bake at 177-191°C for 30 minutes"


def test_lowercase_350f_handled():
    assert convert_instruction_temperatures("at 350°f", UnitSystem.METRIC) == "at 177°C"


def test_no_temperatures_in_text_unchanged():
    text = "Mix the flour and water until smooth."
    assert convert_instruction_temperatures(text, UnitSystem.METRIC) == text


def test_multiple_temps_in_one_instruction():
    out = convert_instruction_temperatures("Preheat to 350°F. After 20 min reduce to 300°F.", UnitSystem.METRIC)
    assert out == "Preheat to 177°C. After 20 min reduce to 149°C."


def test_word_boundary_does_not_match_vitamin_c():
    text = "Mix in vitamin C powder."
    assert convert_instruction_temperatures(text, UnitSystem.US) == text


def test_word_boundary_does_not_match_350_free():
    text = "350Free range eggs"
    assert convert_instruction_temperatures(text, UnitSystem.METRIC) == text


def test_target_original_returns_input_unchanged():
    text = "Bake at 350°F"
    assert convert_instruction_temperatures(text, UnitSystem.ORIGINAL) == text


def test_us_target_converts_celsius_to_fahrenheit():
    assert convert_instruction_temperatures("Bake at 180°C", UnitSystem.US) == "Bake at 356°F"


def test_imperial_target_converts_to_celsius():
    """Imperial UK kitchens use °C — same as metric direction."""
    assert convert_instruction_temperatures("Bake at 350°F", UnitSystem.IMPERIAL) == "Bake at 177°C"


def test_already_correct_unit_passes_through():
    """If text is already in target system unit, leave numeric value alone."""
    assert convert_instruction_temperatures("Bake at 175°C", UnitSystem.METRIC) == "Bake at 175°C"


def test_none_text_returns_none():
    assert convert_instruction_temperatures(None, UnitSystem.METRIC) is None


def test_empty_text_returns_empty():
    assert convert_instruction_temperatures("", UnitSystem.METRIC) == ""


@pytest.mark.parametrize(
    ("source", "expected_metric"),
    [
        ("212°F", "100°C"),
        ("32°F", "0°C"),
        ("0°F", "-18°C"),
    ],
)
def test_known_temperature_conversions(source, expected_metric):
    assert convert_instruction_temperatures(source, UnitSystem.METRIC) == expected_metric
