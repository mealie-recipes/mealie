import json
from pathlib import Path

import pytest
from services.scrape_services import normalize_data, normalize_instructions

CWD = Path(__file__).parent
RAW_RECIPE_DIR = CWD.joinpath("data", "recipes-raw")

def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )


def raw_recipe_info(file_name: str, num_steps: int) -> dict:
    return {"json_file": RAW_RECIPE_DIR.joinpath(file_name), "num_steps": num_steps} 


class TestScraper:
    # a map specifying multiple argument sets for a test method
    params = {
        "test_normalize_instructions": [
            dict(instructions="A\n\nB\n\nC\n\n"),
            dict(instructions=["A","B","C"]),
            dict(instructions=[{"@type": "HowToStep", "text": "A"},
                               {"@type": "HowToStep", "text": "B"},
                               {"@type": "HowToStep", "text": "C"}]),
        ],  
        "test_normalize_data": [
            raw_recipe_info("best-homemade-salsa-recipe.json", 2),
            raw_recipe_info("blue-cheese-stuffed-turkey-meatballs-with-raspberry-balsamic-glaze-2.json", 3),
            raw_recipe_info("bon_appetit.json", 8),
            raw_recipe_info("chunky-apple-cake.json", 4),
            raw_recipe_info("dairy-free-impossible-pumpkin-pie.json", 7),
            raw_recipe_info("how-to-make-instant-pot-spaghetti.json", 8),
            raw_recipe_info("instant-pot-chicken-and-potatoes.json", 4),
            raw_recipe_info("instant-pot-kerala-vegetable-stew.json", 13),
            raw_recipe_info("jalapeno-popper-dip.json", 4),
            raw_recipe_info("microwave_sweet_potatoes_04783.json", 4),
            raw_recipe_info("moroccan-skirt-steak-with-roasted-pepper-couscous.json", 4),
            raw_recipe_info("Pizza-Knoblauch-Champignon-Paprika-vegan.html.json", 5),
        ]
    }

    def test_normalize_data(self, json_file, num_steps):
        recipe_data = normalize_data(json.load(open(json_file)))
        assert len(recipe_data["recipeInstructions"]) == num_steps

    def test_normalize_instructions(self, instructions):
        assert normalize_instructions(instructions) == [{"text": "A"}, {"text": "B"}, {"text": "C"}]
