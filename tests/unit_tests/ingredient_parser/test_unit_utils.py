import pint
import pytest

from mealie.schema.recipe.recipe_ingredient import CreateIngredientUnit
from mealie.services.parser_services.parser_utils import UnitConverter, UnitNotFound, merge_quantity_and_unit
from tests.utils import random_string


def test_uc_parse_string():
    uc = UnitConverter()
    parsed = uc.parse("cup")

    assert isinstance(parsed, pint.Unit)
    assert (str(parsed)) == "cup"


def test_uc_parse_unit():
    uc = UnitConverter()
    parsed = uc.parse(uc.parse("cup"))

    assert isinstance(parsed, pint.Unit)
    assert (str(parsed)) == "cup"


def test_uc_parse_invalid():
    uc = UnitConverter()
    input_str = random_string()
    parsed = uc.parse(input_str)

    assert not isinstance(parsed, pint.Unit)
    assert parsed == input_str


def test_uc_parse_invalid_strict():
    uc = UnitConverter()
    input_str = random_string()

    with pytest.raises(UnitNotFound):
        uc.parse(input_str, strict=True)


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_can_convert(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pint"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    assert uc.can_convert(unit_1, unit_2)


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_cannot_convert(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pound"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    assert not uc.can_convert(unit_1, unit_2)


def test_cannot_convert_invalid_unit():
    uc = UnitConverter()
    assert not uc.can_convert("cup", random_string())
    assert not uc.can_convert(random_string(), "cup")


def test_can_convert_same_unit():
    uc = UnitConverter()
    assert uc.can_convert("cup", "cup")


def test_can_convert_volume_ounce():
    uc = UnitConverter()
    assert uc.can_convert("ounce", "cup")
    assert uc.can_convert("cup", "ounce")


def test_convert_simple():
    uc = UnitConverter()
    quantity, unit = uc.convert(1, "cup", "pint")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "pint"
    assert quantity == 1 / 2


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_convert_pre_parsed(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pint"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    quantity, unit = uc.convert(1, unit_1, unit_2)
    assert isinstance(unit, pint.Unit)
    assert str(unit) == "pint"
    assert quantity == 1 / 2


def test_convert_weight():
    uc = UnitConverter()
    quantity, unit = uc.convert(16, "ounce", "pound")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "pound"
    assert quantity == 1


def test_convert_zero_quantity():
    uc = UnitConverter()
    quantity, unit = uc.convert(0, "cup", "pint")

    assert isinstance(unit, pint.Unit)
    assert quantity == 0


def test_convert_invalid_unit():
    uc = UnitConverter()

    with pytest.raises(UnitNotFound):
        uc.convert(1, "pound", random_string())


def test_convert_incompatible_units():
    uc = UnitConverter()

    with pytest.raises(pint.errors.DimensionalityError):
        uc.convert(1, "pound", "cup")


def test_convert_volume_ounce():
    uc = UnitConverter()
    quantity, unit = uc.convert(8, "ounce", "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 1


def test_merge_same_unit():
    uc = UnitConverter()
    quantity, unit = uc.merge(1, "cup", 2, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 3


@pytest.mark.parametrize("pre_parse_1", [True, False])
@pytest.mark.parametrize("pre_parse_2", [True, False])
def test_merge_compatible_units(pre_parse_1: bool, pre_parse_2: bool):
    unit_1 = "cup"
    unit_2 = "pint"

    uc = UnitConverter()
    if pre_parse_1:
        unit_1 = uc.parse(unit_1)
    if pre_parse_2:
        unit_2 = uc.parse(unit_2)

    quantity, unit = uc.merge(1, unit_1, 1, unit_2)
    assert isinstance(unit, pint.Unit)
    # 1 cup + 1 pint = 1 cup + 2 cups = 3 cups
    assert quantity == 3


def test_merge_weight_units():
    uc = UnitConverter()
    quantity, unit = uc.merge(8, "ounce", 8, "ounce")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "ounce"
    assert quantity == 16


def test_merge_different_weight_units():
    uc = UnitConverter()
    quantity, unit = uc.merge(1, "pound", 8, "ounce")

    assert isinstance(unit, pint.Unit)
    # 1 pound + 8 ounces = 16 ounces + 8 ounces = 24 ounces
    assert str(unit) == "pound"
    assert quantity == 1.5


def test_merge_zero_quantities():
    uc = UnitConverter()
    quantity, unit = uc.merge(0, "cup", 1, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 1


def test_merge_invalid_unit():
    uc = UnitConverter()

    with pytest.raises(UnitNotFound):
        uc.merge(1, "pound", 1, random_string())


def test_merge_incompatible_units():
    uc = UnitConverter()

    with pytest.raises(pint.errors.DimensionalityError):
        uc.merge(1, "pound", 1, "cup")


def test_merge_negative_quantity():
    uc = UnitConverter()
    quantity, unit = uc.merge(-1, "cup", 2, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "cup"
    assert quantity == 1


def test_merge_volume_ounce():
    uc = UnitConverter()
    quantity, unit = uc.merge(4, "ounce", 1, "cup")

    assert isinstance(unit, pint.Unit)
    assert str(unit) == "fluid_ounce"  # converted automatically from ounce
    assert quantity == 12


def test_merge_quantity_and_unit_simple():
    unit_1 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(1, unit_1, 2, unit_2)

    assert quantity == 3
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_invalid():
    unit_1 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")
    unit_2 = CreateIngredientUnit(name="mealie_random", standard_quantity=1, standard_unit=random_string())

    with pytest.raises(UnitNotFound):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_compatible():
    unit_1 = CreateIngredientUnit(name="mealie_pint", standard_quantity=1, standard_unit="pint")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(1, unit_1, 1, unit_2)

    # 1 pint + 1 cup = 2 pints + 1 cup = 3 cups, converted to pint = 1.5 pint
    assert quantity == 1.5
    assert unit.name == "mealie_pint"


def test_merge_quantity_and_unit_selects_larger_unit():
    unit_1 = CreateIngredientUnit(name="mealie_pint", standard_quantity=1, standard_unit="pint")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(2, unit_1, 4, unit_2)

    # 2 pint + 4 cup = 4 cups + 4 cups = 8 cups, should be returned as pint (larger unit)
    assert quantity == 4
    assert unit.name == "mealie_pint"


def test_merge_quantity_and_unit_selects_smaller_unit():
    unit_1 = CreateIngredientUnit(name="mealie_pint", standard_quantity=1, standard_unit="pint")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(0.125, unit_1, 0.5, unit_2)

    # 0.125 pint + 0.5 cup = 0.25 cup + 0.5 cup = 0.75 cup, should be returned as cup (smaller for < 1)
    assert quantity == 0.75
    assert unit.name == "mealie_cup"


def test_merge_quantity_and_unit_missing_standard_data():
    unit_1 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")
    unit_2 = CreateIngredientUnit(name="mealie_cup_no_std", standard_quantity=None, standard_unit=None)

    with pytest.raises(ValueError):
        merge_quantity_and_unit(1, unit_1, 1, unit_2)


def test_merge_quantity_and_unit_volume_ounce():
    unit_1 = CreateIngredientUnit(name="mealie_oz", standard_quantity=1, standard_unit="ounce")
    unit_2 = CreateIngredientUnit(name="mealie_cup", standard_quantity=1, standard_unit="cup")

    quantity, unit = merge_quantity_and_unit(8, unit_1, 1, unit_2)

    assert quantity == 2
    assert unit.name == "mealie_cup"
