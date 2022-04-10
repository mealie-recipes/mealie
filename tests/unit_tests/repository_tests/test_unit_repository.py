from mealie.repos.repository_factory import AllRepositories
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, SaveIngredientUnit
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_unit_merger(database: AllRepositories, unique_user: TestUser):
    slug1 = random_string(10)

    unit_1 = database.ingredient_units.create(
        SaveIngredientUnit(
            name=random_string(10),
            group_id=unique_user.group_id,
        )
    )

    unit_2 = database.ingredient_units.create(
        SaveIngredientUnit(
            name=random_string(10),
            group_id=unique_user.group_id,
        )
    )

    recipe = database.recipes.create(
        Recipe(
            name=slug1,
            user_id=unique_user.group_id,
            group_id=unique_user.group_id,
            recipe_ingredient=[
                RecipeIngredient(note="", unit=unit_1),  # type: ignore
                RecipeIngredient(note="", unit=unit_2),  # type: ignore
            ],
        )  # type: ignore
    )

    # Santiy check make sure recipe got created
    assert recipe.id is not None

    for ing in recipe.recipe_ingredient:
        assert ing.unit.id in [unit_1.id, unit_2.id]  # type: ignore

    database.ingredient_units.merge(unit_2.id, unit_1.id)

    recipe = database.recipes.get_one(recipe.slug)

    for ingredient in recipe.recipe_ingredient:
        assert ingredient.unit.id == unit_1.id  # type: ignore
