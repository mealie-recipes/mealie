from datetime import UTC, datetime

from mealie.schema.household.group_shopping_list import ShoppingListItemCreate, ShoppingListItemOut, ShoppingListSave
from mealie.services.scheduler.tasks.delete_old_checked_shopping_list_items import (
    MAX_CHECKED_ITEMS,
    delete_old_checked_list_items,
)
from tests.utils.factories import random_int, random_string
from tests.utils.fixture_schemas import TestUser


def test_cleanup(unique_user: TestUser):
    database = unique_user.repos
    list_repo = database.group_shopping_lists
    list_item_repo = database.group_shopping_list_item

    shopping_list = list_repo.create(
        ShoppingListSave(
            name=random_string(),
            group_id=unique_user.group_id,
            user_id=unique_user.user_id,
        )
    )
    unchecked_items = list_item_repo.create_many(
        [
            ShoppingListItemCreate(note=random_string(), shopping_list_id=shopping_list.id)
            for _ in range(random_int(MAX_CHECKED_ITEMS + 10, MAX_CHECKED_ITEMS + 20))
        ]
    )

    # create them one at a time so the update timestamps are different
    checked_items: list[ShoppingListItemOut] = []
    for _ in range(random_int(MAX_CHECKED_ITEMS + 10, MAX_CHECKED_ITEMS + 20)):
        new_item = list_item_repo.create(
            ShoppingListItemCreate(note=random_string(), shopping_list_id=shopping_list.id)
        )
        new_item.checked = True
        checked_items.append(list_item_repo.update(new_item.id, new_item))

    # make sure we see all items
    shopping_list = list_repo.get_one(shopping_list.id)  # type: ignore
    assert shopping_list
    assert len(shopping_list.list_items) == len(unchecked_items) + len(checked_items)
    for item in unchecked_items + checked_items:
        assert item in shopping_list.list_items

    checked_items.sort(key=lambda x: x.updated_at or datetime.now(UTC), reverse=True)
    expected_kept_items = unchecked_items + checked_items[:MAX_CHECKED_ITEMS]
    expected_deleted_items = checked_items[MAX_CHECKED_ITEMS:]

    # make sure we only see the expected items
    delete_old_checked_list_items()
    database.session.commit()
    shopping_list = list_repo.get_one(shopping_list.id)  # type: ignore
    assert shopping_list
    assert len(shopping_list.list_items) == len(expected_kept_items)
    for item in expected_kept_items:
        assert item in shopping_list.list_items
    for item in expected_deleted_items:
        assert item not in shopping_list.list_items


def test_no_cleanup(unique_user: TestUser):
    database = unique_user.repos
    list_repo = database.group_shopping_lists
    list_item_repo = database.group_shopping_list_item

    shopping_list = list_repo.create(
        ShoppingListSave(
            name=random_string(),
            group_id=unique_user.group_id,
            user_id=unique_user.user_id,
        )
    )
    unchecked_items = list_item_repo.create_many(
        [
            ShoppingListItemCreate(note=random_string(), shopping_list_id=shopping_list.id)
            for _ in range(MAX_CHECKED_ITEMS)
        ]
    )

    # create them one at a time so the update timestamps are different
    checked_items: list[ShoppingListItemOut] = []
    for _ in range(MAX_CHECKED_ITEMS):
        new_item = list_item_repo.create(
            ShoppingListItemCreate(note=random_string(), shopping_list_id=shopping_list.id)
        )
        new_item.checked = True
        checked_items.append(list_item_repo.update(new_item.id, new_item))

    # make sure we see all items
    shopping_list = list_repo.get_one(shopping_list.id)  # type: ignore
    assert shopping_list
    assert len(shopping_list.list_items) == len(unchecked_items) + len(checked_items)
    for item in unchecked_items + checked_items:
        assert item in shopping_list.list_items

    # make sure we still see all items
    delete_old_checked_list_items()
    database.session.commit()
    shopping_list = list_repo.get_one(shopping_list.id)  # type: ignore
    assert shopping_list
    assert len(shopping_list.list_items) == len(unchecked_items) + len(checked_items)
    for item in unchecked_items + checked_items:
        assert item in shopping_list.list_items
