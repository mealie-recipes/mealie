import json
from pathlib import Path

import pytest
from services.scrape_services import normalize_data, normalize_instructions

CWD = Path(__file__).parent
RAW_RECIPE_DIR = CWD.joinpath("data", "recipes-raw")


@pytest.mark.parametrize("json_file,num_steps", [
    ("best-homemade-salsa-recipe.json", 2),
    ("blue-cheese-stuffed-turkey-meatballs-with-raspberry-balsamic-glaze-2.json", 3),
    ("bon_appetit.json", 8),
    ("chunky-apple-cake.json", 4),
    ("dairy-free-impossible-pumpkin-pie.json", 7),
    ("how-to-make-instant-pot-spaghetti.json", 8),
    ("instant-pot-chicken-and-potatoes.json", 4),
    ("instant-pot-kerala-vegetable-stew.json", 13),
    ("jalapeno-popper-dip.json", 4),
    ("microwave_sweet_potatoes_04783.json", 4),
    ("moroccan-skirt-steak-with-roasted-pepper-couscous.json", 4),
    ("Pizza-Knoblauch-Champignon-Paprika-vegan.html.json", 3),
])
def test_normalize_data(json_file, num_steps):
    recipe_data = normalize_data(json.load(open(RAW_RECIPE_DIR.joinpath(json_file))))
    assert len(recipe_data["recipeInstructions"]) == num_steps


@pytest.mark.parametrize("instructions", [
    "A\n\nB\n\nC\n\n",
    "A\nB\nC\n",
    "A\r\n\r\nB\r\n\r\nC\r\n\r\n",
    "A\r\nB\r\nC\r\n",
    ["A","B","C"],
    [{"@type": "HowToStep", "text": x} for x in ["A","B","C"]]
])
def test_normalize_instructions(instructions):
    assert normalize_instructions(instructions) == [{"text": "A"}, {"text": "B"}, {"text": "C"}]
