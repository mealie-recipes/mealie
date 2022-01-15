import sqlalchemy
from pytest import fixture

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from tests.utils.factories import random_string
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


@fixture(scope="function")
def recipe_ingredient_only(database: AllRepositories):
    # Create a recipe
    recipe = Recipe(
        name=random_string(10),
        recipe_ingredient=[
            RecipeIngredient(note="Ingredient 1"),
            RecipeIngredient(note="Ingredient 2"),
            RecipeIngredient(note="Ingredient 3"),
            RecipeIngredient(note="Ingredient 4"),
            RecipeIngredient(note="Ingredient 5"),
            RecipeIngredient(note="Ingredient 6"),
        ],
    )

    model = database.recipes.create(recipe)

    yield model

    try:
        database.recipes.delete(model.id)
    except sqlalchemy.exc.NoResultFound:  # Entry Deleted in Test
        pass
