from uuid import UUID

import sqlalchemy as sa

from mealie.db.models.recipe.ingredient import IngredientFoodSubstitutionModel
from mealie.schema.household.group_shopping_list import ShoppingListItemCreate, ShoppingListSave
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFoodSubstitution,
    IngredientFood,
    RecipeIngredient,
    SaveIngredientFood,
)
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


def create_food_with_substitutions(user: TestUser, *, substitutions=None) -> IngredientFood:
    return user.repos.ingredient_foods.create(
        SaveIngredientFood(
            name=random_string(10),
            group_id=user.group_id,
            substitutions=substitutions or [],
        )
    )


def substitution_pairs(user: TestUser, food_id) -> set[tuple]:
    """The (substitute food id, note) pairs currently stored against a food."""

    food = user.repos.ingredient_foods.get_one(food_id)
    assert food
    return {(sub.substitute_food_id, sub.note) for sub in food.substitutions}


def count_edges_touching(user: TestUser, food_id) -> int:
    stmt = (
        sa.select(sa.func.count())
        .select_from(IngredientFoodSubstitutionModel)
        .where(
            sa.or_(
                IngredientFoodSubstitutionModel.food_id == food_id,
                IngredientFoodSubstitutionModel.substitute_food_id == food_id,
            )
        )
    )
    return user.repos.session.execute(stmt).scalar_one()


def test_food_merger_moves_outbound_substitutions(unique_user: TestUser):
    """`from -> S` becomes `to -> S`, rather than being deleted along with the merged-away food."""

    target = create_food_with_substitutions(unique_user)
    substitute = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(
        unique_user, substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=substitute.id)]
    )

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert substitution_pairs(unique_user, target.id) == {(substitute.id, None)}


def test_food_merger_repoints_inbound_substitutions(unique_user: TestUser):
    """`X -> from` becomes `X -> to`, or the edge is left pointing at a food that no longer exists."""

    target = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(unique_user)
    referrer = create_food_with_substitutions(
        unique_user, substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=source.id)]
    )

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert substitution_pairs(unique_user, referrer.id) == {(target.id, None)}


def test_food_merger_drops_resulting_self_edges(unique_user: TestUser):
    """
    `from -> to` and `to -> from` both collapse into `to -> to` once the foods are one. This is
    the case a naive implementation ships broken.
    """

    target = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(
        unique_user, substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=target.id)]
    )
    unique_user.repos.ingredient_foods.update(
        target.id,
        SaveIngredientFood(
            id=target.id,
            name=target.name,
            group_id=unique_user.group_id,
            substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=source.id)],
        ),
    )

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert substitution_pairs(unique_user, target.id) == set()
    assert count_edges_touching(unique_user, target.id) == 0


def test_food_merger_collapses_duplicate_substitutions(unique_user: TestUser):
    """Repointing must not produce a second `to -> S` and violate the unique constraint."""

    substitute = create_food_with_substitutions(unique_user)
    target = create_food_with_substitutions(
        unique_user, substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=substitute.id, note="keep me")]
    )
    source = create_food_with_substitutions(
        unique_user, substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=substitute.id, note="drop me")]
    )

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert substitution_pairs(unique_user, target.id) == {(substitute.id, "keep me")}


def test_food_merger_keeps_note_only_substitutions(unique_user: TestUser):
    """Note-only edges carry no food reference, so nothing about a merge can invalidate them."""

    target = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(
        unique_user,
        substitutions=[
            CreateIngredientFoodSubstitution(note="water and a bouillon cube"),
            CreateIngredientFoodSubstitution(note="half butter half applesauce"),
        ],
    )

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert substitution_pairs(unique_user, target.id) == {
        (None, "water and a bouillon cube"),
        (None, "half butter half applesauce"),
    }


def test_food_delete_leaves_no_orphaned_substitutions(unique_user: TestUser):
    """Deleting a food must clean up edges in both directions, not just the ones it owns."""

    substitute = create_food_with_substitutions(unique_user)
    doomed = create_food_with_substitutions(
        unique_user,
        substitutions=[
            CreateIngredientFoodSubstitution(substitute_food_id=substitute.id),
            CreateIngredientFoodSubstitution(note="a textual workaround"),
        ],
    )
    referrer = create_food_with_substitutions(
        unique_user, substitutions=[CreateIngredientFoodSubstitution(substitute_food_id=doomed.id)]
    )

    unique_user.repos.ingredient_foods.delete(doomed.id)

    assert count_edges_touching(unique_user, doomed.id) == 0
    assert substitution_pairs(unique_user, referrer.id) == set()
    assert substitution_pairs(unique_user, substitute.id) == set()
