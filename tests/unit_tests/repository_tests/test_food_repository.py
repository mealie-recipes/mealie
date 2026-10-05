from uuid import UUID

import pytest
import sqlalchemy as sa

from mealie.db.models.recipe.ingredient import IngredientFoodSubstitutionModel
from mealie.schema.household.group_shopping_list import ShoppingListItemCreate, ShoppingListSave
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_ingredient import (
    CreateIngredientFoodSubstitution,
    IngredientFood,
    RecipeIngredient,
    RecipeIngredientSubstitution,
    SaveIngredientFood,
)
from mealie.services.household_services.shopping_lists import ShoppingListService
from tests.utils import api_routes
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
    """`X -> from` becomes `X -> to`, or it is left pointing at a food that no longer exists."""

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
    """Note-only substitutions carry no food reference, so nothing about a merge can invalidate them."""

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
    """Deleting a food must clean up substitutions in both directions, not just the ones it owns."""

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
    assert substitution_pairs(unique_user, referrer.id) == {(None, doomed.name)}
    assert substitution_pairs(unique_user, substitute.id) == set()


def create_recipe_with_ingredient(
    user: TestUser, food: IngredientFood | None, substitute_food_ids: list | None = None
) -> Recipe:
    return user.repos.recipes.create(
        Recipe(
            name=random_string(10),
            user_id=user.user_id,
            group_id=UUID(user.group_id),
            recipe_ingredient=[
                RecipeIngredient(
                    note="",
                    food=food,  # type: ignore
                    substitutions=[
                        RecipeIngredientSubstitution(substitute_food_id=food_id)
                        for food_id in substitute_food_ids or []
                    ],
                )
            ],
        )  # type: ignore
    )


def recipe_substitute_ids(user: TestUser, recipe: Recipe) -> list:
    """The substitute food ids stored against the recipe's only ingredient."""

    stored = user.repos.recipes.get_one(recipe.slug)
    assert stored
    return [sub.substitute_food_id for sub in stored.recipe_ingredient[0].substitutions]


def test_food_delete_preserves_recipe_substitutions_as_text(unique_user: TestUser):
    """
    A food used only as a recipe-level substitute is still a reference. Left behind it points at
    a row that is gone, which renders as an empty substitutions popover and breaks the delete
    outright on Postgres, where the foreign key is enforced.
    """

    food = create_food_with_substitutions(unique_user)
    doomed = create_food_with_substitutions(unique_user)
    recipe = create_recipe_with_ingredient(unique_user, food, [doomed.id])

    assert recipe_substitute_ids(unique_user, recipe) == [doomed.id]

    unique_user.repos.ingredient_foods.delete(doomed.id)

    assert recipe_substitute_ids(unique_user, recipe) == [None]
    saved = unique_user.repos.recipes.get_one(recipe.slug)
    assert saved.recipe_ingredient[0].substitutions[0].note == doomed.name


def test_food_merger_repoints_recipe_substitutions(unique_user: TestUser):
    """`ingredient -> from` becomes `ingredient -> to`, rather than dying with the merged-away food."""

    food = create_food_with_substitutions(unique_user)
    target = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(unique_user)
    recipe = create_recipe_with_ingredient(unique_user, food, [source.id])

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert recipe_substitute_ids(unique_user, recipe) == [target.id]


def test_food_merger_drops_resulting_recipe_self_substitutions(unique_user: TestUser):
    """
    An ingredient calling for one of the two foods and substituting the other ends up telling the
    reader to replace a food with itself, in both directions.
    """

    target = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(unique_user)
    substituting_source = create_recipe_with_ingredient(unique_user, target, [source.id])
    substituting_target = create_recipe_with_ingredient(unique_user, source, [target.id])

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert recipe_substitute_ids(unique_user, substituting_source) == []
    assert recipe_substitute_ids(unique_user, substituting_target) == []


def test_food_merger_collapses_duplicate_recipe_substitutions(unique_user: TestUser):
    """Repointing must not leave the same substitute listed twice on one ingredient."""

    food = create_food_with_substitutions(unique_user)
    target = create_food_with_substitutions(unique_user)
    source = create_food_with_substitutions(unique_user)
    recipe = create_recipe_with_ingredient(unique_user, food, [target.id, source.id])

    unique_user.repos.ingredient_foods.merge(source.id, target.id)

    assert recipe_substitute_ids(unique_user, recipe) == [target.id]


def create_food_snapshot_references(user: TestUser):
    repos = user.repos
    food = repos.ingredient_foods.create(
        SaveIngredientFood(
            name=random_string(10),
            plural_name="tomatoes",
            description="fresh",
            extras={"origin": "garden"},
            group_id=user.group_id,
        )
    )
    recipe = repos.recipes.create(
        Recipe(
            name=random_string(10),
            user_id=user.user_id,
            group_id=UUID(user.group_id),
            recipe_ingredient=[RecipeIngredient(quantity=2, food=food, note="diced", original_text="two tomatoes")],
        )
    )
    shopping_list = repos.group_shopping_lists.create(
        ShoppingListSave(
            name=random_string(10),
            group_id=user.group_id,
            user_id=user.user_id,
        )
    )
    item = repos.group_shopping_list_item.create(
        ShoppingListItemCreate(
            shopping_list_id=shopping_list.id,
            quantity=2,
            food_id=food.id,
            note="diced",
        )
    )
    return food, recipe, shopping_list, item


@pytest.mark.parametrize("bulk", [False, True])
def test_delete_preserves_recipe_and_list_and_roundtrip(unique_user: TestUser, bulk: bool):
    repos = unique_user.repos
    food, original, shopping_list, item = create_food_snapshot_references(unique_user)
    if bulk:
        repos.ingredient_foods.delete_many([food.id])
    else:
        repos.ingredient_foods.delete(food.id)
    repos.ingredient_foods.session.expire_all()
    recipe = repos.recipes.get_one(original.slug)
    ingredient = recipe.recipe_ingredient[0]
    assert ingredient.food is None
    assert ingredient.food_snapshot.name == food.name
    assert ingredient.food_snapshot.plural_name == "tomatoes"
    assert ingredient.food_snapshot.extras == {"origin": "garden"}
    assert ingredient.quantity == 2
    assert ingredient.note == "diced"
    assert ingredient.original_text == "two tomatoes"
    assert ingredient.reference_id == original.recipe_ingredient[0].reference_id
    assert "tomatoes" in ingredient.display
    recipe.recipe_ingredient[0].quantity = 4
    recipe = repos.recipes.update(recipe.slug, recipe)
    assert recipe.recipe_ingredient[0].food is None
    assert recipe.recipe_ingredient[0].food_snapshot.name == food.name
    assert recipe.recipe_ingredient[0].quantity == 4
    saved_item = repos.group_shopping_list_item.get_one(item.id)
    assert saved_item.food is None and saved_item.food_id is None
    assert saved_item.food_snapshot.name == food.name
    assert saved_item.quantity == 2 and saved_item.note == "diced"
    saved_item = repos.group_shopping_list_item.update(saved_item.id, saved_item)
    assert saved_item.food_snapshot.name == food.name
    service = ShoppingListService(repos)
    new_items = service.get_shopping_list_items_from_recipe(shopping_list.id, recipe.id, 1)
    assert new_items[0].food_id is None
    assert new_items[0].food_snapshot.name == food.name
    other = new_items[0].model_copy(deep=True)
    other.food_snapshot.name = "onion"
    assert not service.can_merge(new_items[0], other)
    assert service.can_merge(new_items[0], new_items[0].model_copy(deep=True))


def test_stale_recipe_save_keeps_deleted_food_detached(unique_user: TestUser):
    food, stale_recipe, _, _ = create_food_snapshot_references(unique_user)
    unique_user.repos.ingredient_foods.delete(food.id)
    updated = unique_user.repos.recipes.update(stale_recipe.slug, stale_recipe)
    assert updated.recipe_ingredient[0].food is None
    assert updated.recipe_ingredient[0].food_snapshot.name == food.name


def test_delete_rolls_back_snapshot_writes(unique_user: TestUser, monkeypatch):
    food, recipe, _, item = create_food_snapshot_references(unique_user)
    repo = unique_user.repos.ingredient_foods

    def fail_commit():
        raise RuntimeError("simulated commit failure")

    with monkeypatch.context() as patch:
        patch.setattr(repo.session, "commit", fail_commit)
        with pytest.raises(RuntimeError, match="simulated"):
            repo.delete(food.id)
    restored = unique_user.repos.recipes.get_one(recipe.slug).recipe_ingredient[0]
    assert restored.food.id == food.id
    assert restored.food_snapshot is None
    assert unique_user.repos.group_shopping_list_item.get_one(item.id).food_id == food.id


def test_selecting_new_food_clears_snapshot(unique_user: TestUser):
    food, recipe, _, _ = create_food_snapshot_references(unique_user)
    repos = unique_user.repos
    repos.ingredient_foods.delete(food.id)
    recipe = repos.recipes.get_one(recipe.slug)
    replacement = repos.ingredient_foods.create(
        SaveIngredientFood(name=random_string(10), group_id=unique_user.group_id)
    )
    recipe.recipe_ingredient[0].food = replacement
    saved = repos.recipes.update(recipe.slug, recipe)
    assert saved.recipe_ingredient[0].food.id == replacement.id
    assert saved.recipe_ingredient[0].food_snapshot is None


def test_bulk_delete_preserves_multiple_foods(unique_user: TestUser):
    first, recipe1, _, _ = create_food_snapshot_references(unique_user)
    second, recipe2, _, _ = create_food_snapshot_references(unique_user)
    repos = unique_user.repos
    repos.ingredient_foods.delete_many([first.id, second.id])
    assert repos.recipes.get_one(recipe1.slug).recipe_ingredient[0].food_snapshot.name == first.name
    assert repos.recipes.get_one(recipe2.slug).recipe_ingredient[0].food_snapshot.name == second.name


def test_api_delete_keeps_ingredient_data(api_client, unique_user: TestUser):
    food, recipe, _, _ = create_food_snapshot_references(unique_user)
    response = api_client.delete(api_routes.foods_item_id(food.id), headers=unique_user.token)
    assert response.status_code == 200
    unique_user.repos.ingredient_foods.session.expire_all()
    saved = unique_user.repos.recipes.get_one(recipe.slug).recipe_ingredient[0]
    assert saved.food is None and saved.food_snapshot.name == food.name
    assert api_client.get(api_routes.foods_item_id(food.id), headers=unique_user.token).status_code == 404


def test_inherited_substitutions_survive_food_deletion(unique_user: TestUser):
    food, recipe, _, _ = create_food_snapshot_references(unique_user)
    repos = unique_user.repos
    food.substitutions = [CreateIngredientFoodSubstitution(note="use canned tomatoes")]
    repos.ingredient_foods.update(food.id, food.cast(SaveIngredientFood, group_id=unique_user.group_id))
    repos.ingredient_foods.delete(food.id)
    saved = repos.recipes.get_one(recipe.slug).recipe_ingredient[0]
    assert [sub.note for sub in saved.substitutions] == ["use canned tomatoes"]


def test_stale_shopping_list_save_does_not_restore_food(unique_user: TestUser):
    food, _, _, stale_item = create_food_snapshot_references(unique_user)
    repos = unique_user.repos
    repos.ingredient_foods.delete(food.id)
    saved = repos.group_shopping_list_item.update(stale_item.id, stale_item)
    assert saved.food_id is None and saved.food is None
    assert saved.food_snapshot.name == food.name
    assert repos.ingredient_foods.get_one(food.id) is None


def test_id_only_stale_shopping_write_rolls_back(unique_user: TestUser):
    food, _, _, item = create_food_snapshot_references(unique_user)
    repos = unique_user.repos
    repos.ingredient_foods.delete(food.id)
    stale_data = item.model_dump()
    stale_data["food"] = None
    with pytest.raises(ValueError, match="no longer exists"):
        repos.group_shopping_list_item.update(item.id, stale_data)
    repos.group_shopping_list_item.session.rollback()
    assert repos.group_shopping_list_item.get_one(item.id).food_snapshot.name == food.name


def test_other_group_cannot_delete_or_detach_food(api_client, unique_user: TestUser, g2_user: TestUser):
    food, recipe, _, _ = create_food_snapshot_references(unique_user)
    response = api_client.delete(api_routes.foods_item_id(food.id), headers=g2_user.token)
    assert response.status_code in (403, 404)
    assert g2_user.repos.ingredient_foods.delete_many([food.id]) == []
    unique_user.repos.ingredient_foods.session.expire_all()
    saved = unique_user.repos.recipes.get_one(recipe.slug).recipe_ingredient[0]
    assert saved.food.id == food.id and saved.food_snapshot is None
