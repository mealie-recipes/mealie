import json
import re

import pytest
from mealie.services.scraper.cleaner import Cleaner
from mealie.services.scraper.scraper import extract_recipe_from_html
from tests.test_config import TEST_RAW_HTML, TEST_RAW_RECIPES

# https://github.com/django/django/blob/stable/1.3.x/django/core/validators.py#L45
url_validation_regex = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)$",
    re.IGNORECASE,
)


@pytest.mark.parametrize(
    "json_file,num_steps",
    [
        ("best-homemade-salsa-recipe.json", 2),
        (
            "blue-cheese-stuffed-turkey-meatballs-with-raspberry-balsamic-glaze-2.json",
            3,
        ),
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
    ],
)
def test_cleaner_clean(json_file, num_steps):
    recipe_data = Cleaner.clean(json.load(open(TEST_RAW_RECIPES.joinpath(json_file))))
    assert len(recipe_data["recipeInstructions"]) == num_steps


def test_clean_category():
    assert Cleaner.category("my-category") == ["my-category"]


def test_clean_html():
    assert Cleaner.html("<div>Hello World</div>") == "Hello World"


def test_clean_image():
    assert Cleaner.image(None) == "no image"
    assert Cleaner.image("https://my.image/path/") == "https://my.image/path/"
    assert Cleaner.image({"url": "My URL!"}) == "My URL!"
    assert Cleaner.image(["My URL!", "MY SECOND URL"]) == "My URL!"


@pytest.mark.parametrize(
    "instructions",
    [
        "A\n\nB\n\nC\n\n",
        "A\nB\nC\n",
        "A\r\n\r\nB\r\n\r\nC\r\n\r\n",
        "A\r\nB\r\nC\r\n",
        ["A", "B", "C"],
        [{"@type": "HowToStep", "text": x} for x in ["A", "B", "C"]],
    ],
)
def test_cleaner_instructions(instructions):
    assert Cleaner.instructions(instructions) == [
        {"text": "A"},
        {"text": "B"},
        {"text": "C"},
    ]


def test_html_with_recipe_data():
    path = TEST_RAW_HTML.joinpath("healthy_pasta_bake_60759.html")
    url = "https://www.bbc.co.uk/food/recipes/healthy_pasta_bake_60759"
    recipe_data = extract_recipe_from_html(open(path).read(), url)

    assert len(recipe_data["name"]) > 10
    assert len(recipe_data["slug"]) > 10
    assert recipe_data["orgURL"] == url
    assert len(recipe_data["description"]) > 100
    assert url_validation_regex.match(recipe_data["image"])
    assert len(recipe_data["recipeIngredient"]) == 13
    assert len(recipe_data["recipeInstructions"]) == 4


def test_time_cleaner():

    my_time_delta = "PT2H30M"
    return_delta = Cleaner.time(my_time_delta)

    assert return_delta == "2 Hours 30 Minutes"
