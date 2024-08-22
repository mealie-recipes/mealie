import pytest
import sqlalchemy
from pydantic import UUID4

from mealie.schema.household.group_shopping_list import ShoppingListItemCreate, ShoppingListOut, ShoppingListSave
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def create_item(list_id: UUID4) -> dict:
    return {
        "shopping_list_id": str(list_id),
        "checked": False,
        "position": 0,
        "is_food": False,
        "note": random_string(10),
        "quantity": 1,
        "unit_id": None,
        "food_id": None,
        "recipe_id": None,
        "label_id": None,
    }


@pytest.fixture(scope="function")
def shopping_lists(unique_user: TestUser):
    database = unique_user.repos
    models: list[ShoppingListOut] = []

    for _ in range(3):
        model = database.group_shopping_lists.create(
            ShoppingListSave(
                name=random_string(10),
                group_id=unique_user.group_id,
                user_id=unique_user.user_id,
            ),
        )

        models.append(model)

    yield models

    for model in models:
        try:
            database.group_shopping_lists.delete(model.id)
        except Exception:  # Entry Deleted in Test
            pass


@pytest.fixture(scope="function")
def shopping_list(unique_user: TestUser):
    database = unique_user.repos
    model = database.group_shopping_lists.create(
        ShoppingListSave(
            name=random_string(10),
            group_id=unique_user.group_id,
            user_id=unique_user.user_id,
        ),
    )

    yield model

    try:
        database.group_shopping_lists.delete(model.id)
    except Exception:  # Entry Deleted in Test
        pass


@pytest.fixture(scope="function")
def list_with_items(unique_user: TestUser):
    database = unique_user.repos
    list_model = database.group_shopping_lists.create(
        ShoppingListSave(
            name=random_string(10),
            group_id=unique_user.group_id,
            user_id=unique_user.user_id,
        ),
    )

    for _ in range(10):
        database.group_shopping_list_item.create(
            ShoppingListItemCreate(
                **create_item(list_model.id),
            )
        )

    # refresh model
    list_model = database.group_shopping_lists.get_one(list_model.id)  # type: ignore

    yield list_model

    try:
        database.group_shopping_lists.delete(list_model.id)
    except sqlalchemy.exc.NoResultFound:  # Entry Deleted in Test
        pass
