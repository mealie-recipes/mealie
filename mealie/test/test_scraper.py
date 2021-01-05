import pytest
import json
import os
from pprint import pprint

from services.scrape_services import normalize_data, normalize_instructions

TEST_DATA_DIR = os.getenv("TEST_DATA_DIR")

def pytest_generate_tests(metafunc):
    # called once per each test function
    funcarglist = metafunc.cls.params[metafunc.function.__name__]
    argnames = sorted(funcarglist[0])
    metafunc.parametrize(
        argnames, [[funcargs[name] for name in argnames] for funcargs in funcarglist]
    )


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
            dict(json_file=f"{TEST_DATA_DIR}/best-homemade-salsa-recipe.json", num_steps=2),
            dict(json_file=f"{TEST_DATA_DIR}/blue-cheese-stuffed-turkey-meatballs-with-raspberry-balsamic-glaze-2.json", num_steps=3),
            dict(json_file=f"{TEST_DATA_DIR}/bon_appetit.json", num_steps=8),
            dict(json_file=f"{TEST_DATA_DIR}/chunky-apple-cake.json", num_steps=4),
            dict(json_file=f"{TEST_DATA_DIR}/dairy-free-impossible-pumpkin-pie.json", num_steps=7),
            dict(json_file=f"{TEST_DATA_DIR}/how-to-make-instant-pot-spaghetti.json", num_steps=8),
            dict(json_file=f"{TEST_DATA_DIR}/instant-pot-chicken-and-potatoes.json", num_steps=4),
            dict(json_file=f"{TEST_DATA_DIR}/instant-pot-kerala-vegetable-stew.json", num_steps=13),
            dict(json_file=f"{TEST_DATA_DIR}/jalapeno-popper-dip.json", num_steps=4),
            dict(json_file=f"{TEST_DATA_DIR}/microwave_sweet_potatoes_04783.json", num_steps=4),
            dict(json_file=f"{TEST_DATA_DIR}/moroccan-skirt-steak-with-roasted-pepper-couscous.json", num_steps=4),
            dict(json_file=f"{TEST_DATA_DIR}/Pizza-Knoblauch-Champignon-Paprika-vegan.html.json", num_steps=5),
        ]
    }

    def test_normalize_data(self, json_file, num_steps):
        recipe_data = normalize_data(json.load(open(json_file)))
        assert len(recipe_data["recipeInstructions"]) == num_steps

    def test_normalize_instructions(self, instructions):
        assert normalize_instructions(instructions) == [{"text": "A"}, {"text": "B"}, {"text": "C"}]
