"""Black-box unit tests for clean_ingredients (KacperM). Test cases are documented in kacperM.md."""

import pytest

from mealie.services.scraper.cleaner import clean_ingredients


@pytest.mark.parametrize(
    ("ingredients", "default", "expected"),
    [
        pytest.param(["1 cup flour", "2 eggs"], None, ["1 cup flour", "2 eggs"], id="KM-01"),
        pytest.param("1 cup flour", None, ["1 cup flour"], id="KM-02"),
        pytest.param(None, None, [], id="KM-03"),
        pytest.param(None, ["1 egg"], ["1 egg"], id="KM-04"),
        pytest.param(None, [], [], id="KM-05"),
        pytest.param([], None, [], id="KM-06"),
        pytest.param(["1 egg", "1 egg"], None, ["1 egg", "1 egg"], id="KM-07"),
    ],
)
def test_clean_ingredients(ingredients, default, expected):
    assert clean_ingredients(ingredients, default) == expected


@pytest.mark.parametrize(
    "ingredients",
    [
        pytest.param(123, id="KM-08"),
        pytest.param({"name": "flour"}, id="KM-09"),
        pytest.param(("1 egg",), id="KM-10"),
    ],
)
def test_clean_ingredients_unsupported_type(ingredients):
    try:
        result = clean_ingredients(ingredients)
    except TypeError:
        return
    pytest.fail(f"Nie zgłoszono TypeError, funkcja zwróciła: {result!r}")
