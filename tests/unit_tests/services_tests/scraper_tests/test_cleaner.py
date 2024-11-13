import json
import re
from pathlib import Path

import pytest

from mealie.lang.providers import local_provider
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


@pytest.mark.parametrize("json_file,num_steps", test_cleaner_data)
def test_cleaner_clean(json_file: Path, num_steps):
    translator = local_provider()
    recipe_data = cleaner.clean(json.loads(json_file.read_text()), translator)
    assert len(recipe_data.recipe_instructions or []) == num_steps


def test_html_with_recipe_data():
    path = test_data.html_healthy_pasta_bake_60759
    url = "https://www.bbc.co.uk/food/recipes/healthy_pasta_bake_60759"
    translator = local_provider()

    open_graph_strategy = RecipeScraperOpenGraph(url, translator)

    recipe_data = open_graph_strategy.get_recipe_fields(path.read_text())

    assert len(recipe_data["name"]) > 10
    assert len(recipe_data["slug"]) > 10
    assert recipe_data["orgURL"] == url
    assert len(recipe_data["description"]) > 100
    assert url_validation_regex.match(recipe_data["image"])
