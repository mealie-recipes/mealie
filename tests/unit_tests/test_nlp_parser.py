from dataclasses import dataclass
from fractions import Fraction

import pytest

from mealie.services.scraper.ingredient_nlp.processor import CRFIngredient, convert_list_to_crf_model


@dataclass
class TestIngredient:
    input: str
    quantity: float


test_ingredients = [
    TestIngredient("½ cup all-purpose flour", 0.5),
    TestIngredient("1 ½ teaspoons ground black pepper", 1.5),
    TestIngredient("⅔ cup unsweetened flaked coconut", 0.7),
    TestIngredient("⅓ cup panko bread crumbs", 0.3),
]


@pytest.mark.skip
def test_nlp_parser():
    models: list[CRFIngredient] = convert_list_to_crf_model([x.input for x in test_ingredients])

    # Itterate over mdoels and test_ingreidnets to gether
    print()
    for model, test_ingredient in zip(models, test_ingredients):
        print("Testing:", test_ingredient.input, end="")

        assert float(sum(Fraction(s) for s in model.qty.split())) == test_ingredient.quantity

        print(" ✅ Passed")


if __name__ == "__main__":
    test_nlp_parser()
