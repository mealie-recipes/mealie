from uuid import uuid4

import pytest

from mealie.schema.recipe.recipe_ingredient import IngredientFoodCreate, IngredientFoodSave
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_food_self_parenting_rejected(unique_user: TestUser):
    food_id = uuid4()
    # Pydantic validation rejects self-parenting
    with pytest.raises(ValueError, match="a food cannot be its own parent"):
        IngredientFoodCreate(id=food_id, name="Self Parent", parent_id=food_id)

    # Repository validation also rejects self-parenting on update
    repo = unique_user.repos.ingredient_foods
    food = repo.create(IngredientFoodSave(name=random_string(10), group_id=unique_user.group_id))
    with pytest.raises(ValueError, match="A food cannot be its own parent"):
        repo.update(food.id, {"parent_id": food.id})


def test_food_cross_group_parent_rejected(unique_user: TestUser, g2_user: TestUser):
    repo1 = unique_user.repos.ingredient_foods
    repo2 = g2_user.repos.ingredient_foods

    food_group2 = repo2.create(IngredientFoodSave(name=random_string(10), group_id=g2_user.group_id))

    # User 1 cannot use food from group 2 as parent
    with pytest.raises(ValueError, match="Parent food does not exist in the same group"):
        repo1.create(
            IngredientFoodSave(
                name=random_string(10),
                group_id=unique_user.group_id,
                parent_id=food_group2.id,
            )
        )


def test_food_two_level_depth_limit(unique_user: TestUser):
    repo = unique_user.repos.ingredient_foods

    parent = repo.create(IngredientFoodSave(name="Mushroom", group_id=unique_user.group_id))
    child = repo.create(IngredientFoodSave(name="Porcini", group_id=unique_user.group_id, parent_id=parent.id))

    # 1. A child cannot be selected as a parent (Food -> Child -> Grandchild forbidden)
    with pytest.raises(ValueError, match="maximum 2 levels allowed"):
        repo.create(IngredientFoodSave(name="Baby Porcini", group_id=unique_user.group_id, parent_id=child.id))

    # 2. A food that already has children cannot be given a parent
    grandparent = repo.create(IngredientFoodSave(name="Fungus", group_id=unique_user.group_id))
    with pytest.raises(ValueError, match="maximum 2 levels allowed"):
        repo.update(
            parent.id,
            IngredientFoodSave(
                id=parent.id,
                name=parent.name,
                group_id=unique_user.group_id,
                parent_id=grandparent.id,
            ),
        )


def test_food_get_empty_excludes_parents(unique_user: TestUser):
    repo = unique_user.repos.ingredient_foods

    parent = repo.create(IngredientFoodSave(name="MushroomParent", group_id=unique_user.group_id))
    child = repo.create(IngredientFoodSave(name="PorciniChild", group_id=unique_user.group_id, parent_id=parent.id))
    unused_food = repo.create(IngredientFoodSave(name="UnusedFood", group_id=unique_user.group_id))

    empty_foods = repo.get_empty()
    empty_ids = [f.id for f in empty_foods]

    # The parent food MUST NOT be in empty_foods because it has a child
    assert parent.id not in empty_ids

    # Unused food without children should be included
    assert unused_food.id in empty_ids

    # An unused child food without children of its own is included
    assert child.id in empty_ids


def test_food_delete_leaves_children_parentless(unique_user: TestUser):
    repo = unique_user.repos.ingredient_foods

    parent = repo.create(IngredientFoodSave(name=random_string(10), group_id=unique_user.group_id))
    child = repo.create(IngredientFoodSave(name=random_string(10), group_id=unique_user.group_id, parent_id=parent.id))

    assert child.parent_id == parent.id

    # Deleting parent
    repo.delete(parent.id)

    # Child still exists but parent_id is cleared
    updated_child = repo.get_one(child.id)
    assert updated_child is not None
    assert updated_child.parent_id is None
    assert updated_child.parent is None


def test_food_merge_hierarchy(unique_user: TestUser):
    repo = unique_user.repos.ingredient_foods

    # Scenario 1: Merging parent into another food reassigns children to target
    parent1 = repo.create(IngredientFoodSave(name="Parent 1", group_id=unique_user.group_id))
    parent2 = repo.create(IngredientFoodSave(name="Parent 2", group_id=unique_user.group_id))
    child1 = repo.create(IngredientFoodSave(name="Child 1", group_id=unique_user.group_id, parent_id=parent1.id))

    repo.merge(parent1.id, parent2.id)

    updated_child1 = repo.get_one(child1.id)
    assert updated_child1.parent_id == parent2.id

    # Scenario 2: Merging child into its parent
    child2 = repo.create(IngredientFoodSave(name="Child 2", group_id=unique_user.group_id, parent_id=parent2.id))
    repo.merge(child2.id, parent2.id)

    assert repo.get_one(child2.id) is None
    assert repo.get_one(parent2.id) is not None

    # Scenario 3: Merging parent into child promotes child to top-level parent
    parent3 = repo.create(IngredientFoodSave(name="Parent 3", group_id=unique_user.group_id))
    child3a = repo.create(IngredientFoodSave(name="Child 3A", group_id=unique_user.group_id, parent_id=parent3.id))
    child3b = repo.create(IngredientFoodSave(name="Child 3B", group_id=unique_user.group_id, parent_id=parent3.id))

    # Merge parent3 into child3a
    repo.merge(parent3.id, child3a.id)

    updated_3a = repo.get_one(child3a.id)
    updated_3b = repo.get_one(child3b.id)

    assert updated_3a.parent_id is None  # Became top-level parent
    assert updated_3b.parent_id == child3a.id  # Siblings repointed to child3a
