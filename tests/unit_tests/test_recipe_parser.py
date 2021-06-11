from dataclasses import dataclass

import pytest
from mealie.services.scraper import scraper


@dataclass
class RecipeSiteTestCase:
    url: str
    expected_slug: str
    num_ingredients: int
    num_steps: int


test_cases = [
    RecipeSiteTestCase(
        url="https://www.seriouseats.com/taiwanese-three-cup-chicken-san-bei-gi-recipe",
        expected_slug="taiwanese-three-cup-chicken-san-bei-ji-recipe",
        num_ingredients=10,
        num_steps=3,
    ),
    RecipeSiteTestCase(
        url="https://www.rezeptwelt.de/backen-herzhaft-rezepte/schinken-kaese-waffeln-ohne-viel-schnickschnack/4j0bkiig-94d4d-106529-cfcd2-is97x2ml",
        expected_slug="schinken-kase-waffeln-ohne-viel-schnickschnack",
        num_ingredients=7,
        num_steps=1,  # Malformed JSON Data, can't parse steps just get one string
    ),
    RecipeSiteTestCase(
        url="https://cookpad.com/us/recipes/5544853-sous-vide-smoked-beef-ribs",
        expected_slug="sous-vide-smoked-beef-ribs",
        num_ingredients=7,
        num_steps=12,
    ),
    RecipeSiteTestCase(
        url="https://www.greatbritishchefs.com/recipes/jam-roly-poly-recipe",
        expected_slug="jam-roly-poly-with-custard",
        num_ingredients=13,
        num_steps=9,
    ),
    RecipeSiteTestCase(
        url="https://recipes.anovaculinary.com/recipe/sous-vide-shrimp",
        expected_slug="sous-vide-shrimp",
        num_ingredients=5,
        num_steps=0,
    ),
    RecipeSiteTestCase(
        url="https://www.bonappetit.com/recipe/detroit-style-pepperoni-pizza",
        expected_slug="detroit-style-pepperoni-pizza",
        num_ingredients=8,
        num_steps=5,
    ),
]


@pytest.mark.parametrize("recipe_test_data", test_cases)
def test_recipe_parser(recipe_test_data: RecipeSiteTestCase):
    recipe = scraper.create_from_url(recipe_test_data.url)

    assert recipe.slug == recipe_test_data.expected_slug
    assert len(recipe.recipe_instructions) == recipe_test_data.num_steps
    assert len(recipe.recipe_ingredient) == recipe_test_data.num_ingredients
    assert recipe.org_url == recipe_test_data.url
