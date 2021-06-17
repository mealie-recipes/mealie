import pytest
from mealie.services.scraper import scraper
from tests.utils.recipe_data import RecipeSiteTestCase, get_recipe_test_cases

test_cases = get_recipe_test_cases()

"""
These tests are skipped by default and only really used when troubleshooting the parser
directly. If you are working on improve the parser you can add test cases to the `get_recipe_test_cases` function
and then use this test case by removing the `@pytest.mark.skip` and than testing your results.
"""


@pytest.mark.skip
@pytest.mark.parametrize("recipe_test_data", test_cases)
def test_recipe_parser(recipe_test_data: RecipeSiteTestCase):
    recipe = scraper.create_from_url(recipe_test_data.url)

    assert recipe.slug == recipe_test_data.expected_slug
    assert len(recipe.recipe_instructions) == recipe_test_data.num_steps
    assert len(recipe.recipe_ingredient) == recipe_test_data.num_ingredients
    assert recipe.org_url == recipe_test_data.url
