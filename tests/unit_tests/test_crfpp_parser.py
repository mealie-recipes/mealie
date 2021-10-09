from dataclasses import dataclass
from fractions import Fraction

import pytest

from mealie.services.parser_services.crfpp.processor import CRFIngredient, convert_list_to_crf_model


@dataclass
class TestIngredient:
    input: str
    quantity: float
    unit: str
    food: str
    comments: str


# TODO - add more robust test cases
test_ingredients = [
    TestIngredient("½ cup all-purpose flour", 0.5, "cup", "all-purpose flour", ""),
    TestIngredient("1 ½ teaspoons ground black pepper", 1.5, "teaspoon", "black pepper", "ground"),
    TestIngredient("⅔ cup unsweetened flaked coconut", 0.7, "cup", "coconut", "unsweetened flaked"),
    TestIngredient("⅓ cup panko bread crumbs", 0.3, "cup", "panko bread crumbs", ""),
]


def crf_exists() -> bool:
    import shutil

    return shutil.which("crf_test") is not None


@pytest.mark.skipif(not crf_exists(), reason="CRF++ not installed")
def test_nlp_parser():
    models: list[CRFIngredient] = convert_list_to_crf_model([x.input for x in test_ingredients])

    # Itterate over mdoels and test_ingreidnets to gether
    for model, test_ingredient in zip(models, test_ingredients):
        assert float(sum(Fraction(s) for s in model.qty.split())) == test_ingredient.quantity

        assert model.comment == test_ingredient.comments
        assert model.name == test_ingredient.food
        assert model.unit == test_ingredient.unit
