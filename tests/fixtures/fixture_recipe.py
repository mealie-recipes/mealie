import contextlib
from collections.abc import Generator

import sqlalchemy
from pytest import fixture

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_category import CategoryOut, CategorySave
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient
from mealie.schema.recipe.recipe_step import RecipeStep
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser
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
def recipe_ingredient_only(unique_user: TestUser):
    database = unique_user.repos
    # Create a recipe
    recipe = Recipe(
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
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

    with contextlib.suppress(sqlalchemy.exc.NoResultFound):
        database.recipes.delete(model.slug)


@fixture(scope="function")
def recipe_categories(unique_user: TestUser) -> Generator[list[CategoryOut], None, None]:
    database = unique_user.repos
    models: list[CategoryOut] = []
    for _ in range(3):
        category = CategorySave(
            group_id=unique_user.group_id,
            name=random_string(10),
        )
        model = database.categories.create(category)
        models.append(model)

    yield models

    for m in models:
        with contextlib.suppress(sqlalchemy.exc.NoResultFound):
            database.categories.delete(m.id)


@fixture(scope="function")
def random_recipe(unique_user: TestUser) -> Generator[Recipe, None, None]:
    database = unique_user.repos
    recipe = Recipe(
        user_id=unique_user.user_id,
        group_id=unique_user.group_id,
        name=random_string(10),
        recipe_ingredient=[
            RecipeIngredient(note="Ingredient 1"),
            RecipeIngredient(note="Ingredient 2"),
            RecipeIngredient(note="Ingredient 3"),
        ],
        recipe_instructions=[
            RecipeStep(text="Step 1"),
            RecipeStep(text="Step 2"),
            RecipeStep(text="Step 3"),
        ],
    )

    model = database.recipes.create(recipe)

    yield model

    with contextlib.suppress(sqlalchemy.exc.NoResultFound):
        database.recipes.delete(model.slug)
