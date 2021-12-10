import json
import re
from datetime import timedelta
from pathlib import Path

import pytest

from mealie.services.scraper import cleaner
from mealie.services.scraper.scraper_strategies import RecipeScraperOpenGraph
from tests import data as test_data

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

test_cleaner_data = [
    (test_data.json_best_homemade_salsa_recipe, 2),
    (test_data.json_blue_cheese_stuffed_turkey_meatballs_with_raspberry_balsamic_glaze_2, 3),
    (test_data.json_bon_appetit, 8),
    (test_data.json_chunky_apple_cake, 4),
    (test_data.json_dairy_free_impossible_pumpkin_pie, 7),
    (test_data.json_how_to_make_instant_pot_spaghetti, 8),
    (test_data.json_instant_pot_chicken_and_potatoes, 4),
    (test_data.json_instant_pot_kerala_vegetable_stew, 13),
    (test_data.json_jalapeno_popper_dip, 4),
    (test_data.json_microwave_sweet_potatoes_04783, 4),
    (test_data.json_moroccan_skirt_steak_with_roasted_pepper_couscous, 4),
    (test_data.json_pizza_knoblauch_champignon_paprika_vegan_html, 3),
]


@pytest.mark.parametrize(
    "json_file,num_steps",
    test_cleaner_data,
)
def test_cleaner_clean(json_file: Path, num_steps):
    recipe_data = cleaner.clean(json.loads(json_file.read_text()))
    assert len(recipe_data["recipeInstructions"]) == num_steps


def test_clean_category():
    assert cleaner.category("my-category") == ["my-category"]


def test_clean_string():
    assert cleaner.clean_string("<div>Hello World</div>") == "Hello World"


def test_clean_image():
    assert cleaner.image(None) == "no image"
    assert cleaner.image("https://my.image/path/") == "https://my.image/path/"
    assert cleaner.image({"url": "My URL!"}) == "My URL!"
    assert cleaner.image(["My URL!", "MY SECOND URL"]) == "My URL!"


@pytest.mark.parametrize(
    "nutrition,expected",
    [
        (None, {}),
        ({"calories": "105 kcal"}, {"calories": "105"}),
        ({"calories": "105 kcal 104 sugar"}, {"calories": "105"}),
        ({"calories": ""}, {}),
        ({"calories": ["not just a string"], "sugarContent": "but still tries 555.321"}, {"sugarContent": "555.321"}),
        ({"sodiumContent": "5.1235g"}, {"sodiumContent": "5123.5"}),
        ({"sodiumContent": "5mg"}, {"sodiumContent": "5"}),
        ({"sodiumContent": "10oz"}, {"sodiumContent": "10"}),
        ({"sodiumContent": "10.1.2g"}, {"sodiumContent": "10100.0"}),
    ],
)
def test_clean_nutrition(nutrition, expected):
    assert cleaner.clean_nutrition(nutrition) == expected


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
    assert cleaner.instructions(instructions) == [
        {"text": "A"},
        {"text": "B"},
        {"text": "C"},
    ]


def test_html_with_recipe_data():
    path = test_data.html_healthy_pasta_bake_60759
    url = "https://www.bbc.co.uk/food/recipes/healthy_pasta_bake_60759"

    open_graph_strategy = RecipeScraperOpenGraph(url)

    recipe_data = open_graph_strategy.get_recipe_fields(path.read_text())

    assert len(recipe_data["name"]) > 10
    assert len(recipe_data["slug"]) > 10
    assert recipe_data["orgURL"] == url
    assert len(recipe_data["description"]) > 100
    assert url_validation_regex.match(recipe_data["image"])


@pytest.mark.parametrize(
    "time_delta,expected",
    [
        ("PT2H30M", "2 Hours 30 Minutes"),
        ("PT30M", "30 Minutes"),
        ("PT3H", "3 Hours"),
        ("P1DT1H1M1S", "1 day 1 Hour 1 Minute 1 Second"),
        ("P1DT1H1M1.53S", "1 day 1 Hour 1 Minute 1 Second"),
        ("PT-3H", "PT-3H"),
        ("PT", "none"),
    ],
)
def test_time_cleaner(time_delta, expected):
    assert cleaner.clean_time(time_delta) == expected


@pytest.mark.parametrize(
    "t,max_components,max_decimal_places,expected",
    [
        (timedelta(days=2, seconds=17280), None, 2, "2 days 4 Hours 48 Minutes"),
        (timedelta(days=2, seconds=17280), 1, 2, "2.2 days"),
        (timedelta(days=365), None, 2, "1 year"),
    ],
)
def test_pretty_print_timedelta(t, max_components, max_decimal_places, expected):
    assert cleaner.pretty_print_timedelta(t, max_components, max_decimal_places) == expected
