from dataclasses import dataclass

import pytest
from mealie.services.scraper import scraper
from tests.utils.recipe_data import get_recipe_test_cases


@dataclass
class RecipeSiteTestCase:
    url: str
    expected_slug: str
    num_ingredients: int
    num_steps: int


test_cases = get_recipe_test_cases()


@pytest.mark.parametrize("recipe_test_data", test_cases)
def test_recipe_parser(recipe_test_data: RecipeSiteTestCase):
    recipe = scraper.create_from_url(recipe_test_data.url)

    assert recipe.slug == recipe_test_data.expected_slug
    assert len(recipe.recipe_instructions) == recipe_test_data.num_steps
    assert len(recipe.recipe_ingredient) == recipe_test_data.num_ingredients
    assert recipe.org_url == recipe_test_data.url
