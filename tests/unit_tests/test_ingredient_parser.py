from dataclasses import dataclass
from fractions import Fraction

import pytest

from mealie.services.parser_services import RegisteredParser, get_parser
from mealie.services.parser_services.crfpp.processor import CRFIngredient, convert_list_to_crf_model


@dataclass
class TestIngredient:
    input: str
    quantity: float
    unit: str
    food: str
    comments: str


def crf_exists() -> bool:
    import shutil

    return shutil.which("crf_test") is not None


# TODO - add more robust test cases
test_ingredients = [
    TestIngredient("½ cup all-purpose flour", 0.5, "cup", "all-purpose flour", ""),
    TestIngredient("1 ½ teaspoons ground black pepper", 1.5, "teaspoon", "black pepper", "ground"),
    TestIngredient("⅔ cup unsweetened flaked coconut", 0.7, "cup", "coconut", "unsweetened flaked"),
    TestIngredient("⅓ cup panko bread crumbs", 0.3, "cup", "panko bread crumbs", ""),
]


@pytest.mark.skipif(not crf_exists(), reason="CRF++ not installed")
def test_nlp_parser():
    models: list[CRFIngredient] = convert_list_to_crf_model([x.input for x in test_ingredients])

    # Itterate over mdoels and test_ingreidnets to gether
    for model, test_ingredient in zip(models, test_ingredients):
        assert float(sum(Fraction(s) for s in model.qty.split())) == test_ingredient.quantity

        assert model.comment == test_ingredient.comments
        assert model.name == test_ingredient.food
        assert model.unit == test_ingredient.unit


def test_brute_parser():
    # input: (quantity, unit, food, comments)
    expectations = {
        # Dutch
        "1 theelepel koffie": (1, "theelepel", "koffie", ""),
        "3 theelepels koffie": (3, "theelepels", "koffie", ""),
        "1 eetlepel tarwe": (1, "eetlepel", "tarwe", ""),
        "20 eetlepels bloem": (20, "eetlepels", "bloem", ""),
        "1 mespunt kaneel": (1, "mespunt", "kaneel", ""),
        "1 snuf(je) zout": (1, "snuf(je)", "zout", ""),
        "2 tbsp minced cilantro, leaves and stems": (2, "tbsp", "minced cilantro", "leaves and stems"),
        "1 large yellow onion, coarsely chopped": (1, "large", "yellow onion", "coarsely chopped"),
        "1 1/2 tsp garam masala": (1.5, "tsp", "garam masala", ""),
        "2 cups mango chunks, (2 large mangoes) (fresh or frozen)": (
            2,
            "cups",
            "mango chunks, (2 large mangoes)",
            "fresh or frozen",
        ),
    }
    parser = get_parser(RegisteredParser.brute)

    for key, val in expectations.items():
        parsed = parser.parse_one(key)

        assert parsed.ingredient.quantity == val[0]
        assert parsed.ingredient.unit.name == val[1]
        assert parsed.ingredient.food.name == val[2]
        assert parsed.ingredient.note in {val[3], None}
