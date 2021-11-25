from pytest import fixture

from tests.utils.recipe_data import get_raw_no_image, get_raw_recipe, get_recipe_test_cases


@fixture(scope="session")
def raw_recipe():
    return get_raw_recipe()


@fixture(scope="session")
def raw_recipe_no_image():
    return get_raw_no_image()


@fixture(scope="session")
def recipe_store():
    return get_recipe_test_cases()
