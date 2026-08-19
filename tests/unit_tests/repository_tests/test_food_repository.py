from uuid import UUID

from mealie.schema.household.group_shopping_list import ShoppingListItemCreate, ShoppingListSave
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import RecipeIngredient, SaveIngredientFood
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_food_merger(unique_user: TestUser):
    recipe: Recipe | None = None
    database = unique_user.repos
    slug1 = random_string(10)

    food_1 = database.ingredient_foods.create(
        SaveIngredientFood(
            name=random_string(10),
            group_id=unique_user.group_id,
        )
    )

    food_2 = database.ingredient_foods.create(
        SaveIngredientFood(
            name=random_string(10),
            group_id=unique_user.group_id,
        )
    )

    recipe = database.recipes.create(
        Recipe(
            name=slug1,
            user_id=unique_user.user_id,
            group_id=UUID(unique_user.group_id),
            recipe_ingredient=[
                RecipeIngredient(note="", food=food_1),  # type: ignore
                RecipeIngredient(note="", food=food_2),  # type: ignore
            ],
        )  # type: ignore
    )

    # Santiy check make sure recipe got created
    assert recipe.id is not None

    for ing in recipe.recipe_ingredient:
        assert ing.food.id in [food_1.id, food_2.id]  # type: ignore

    database.ingredient_foods.merge(food_2.id, food_1.id)

    recipe = database.recipes.get_one(recipe.slug)
    assert recipe

    for ingredient in recipe.recipe_ingredient:
        assert ingredient.food.id == food_1.id  # type: ignore


def test_food_merger_with_shopping_list_reference(unique_user: TestUser):
    """Merging a food that a shopping list item points at should move the reference, not fail."""
    database = unique_user.repos

    food_1 = database.ingredient_foods.create(SaveIngredientFood(name=random_string(10), group_id=unique_user.group_id))
    food_2 = database.ingredient_foods.create(SaveIngredientFood(name=random_string(10), group_id=unique_user.group_id))

    shopping_list = database.group_shopping_lists.create(
        ShoppingListSave(
            name=random_string(10),
            group_id=unique_user.group_id,
            user_id=unique_user.user_id,
        )
    )

    item = database.group_shopping_list_item.create(
        ShoppingListItemCreate(
            shopping_list_id=shopping_list.id,
            note=random_string(10),
            quantity=1,
            food_id=food_2.id,
        )
    )

    database.ingredient_foods.merge(food_2.id, food_1.id)

    updated_item = database.group_shopping_list_item.get_one(item.id)
    assert updated_item
    assert updated_item.food_id == food_1.id
