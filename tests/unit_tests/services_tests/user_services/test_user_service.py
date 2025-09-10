from datetime import UTC, datetime, timedelta

import pytest

from mealie.services.scheduler.tasks.reset_locked_users import locked_user_reset
from mealie.services.user_services.user_service import UserService
from tests.utils.fixture_schemas import TestUser


def test_get_locked_users(user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple
    database = usr_1.repos

    # Setup
    user_service = UserService(database)

    user_1 = database.users.get_one(usr_1.user_id)
    user_2 = database.users.get_one(usr_2.user_id)
    assert user_1 and user_2

    locked_users = user_service.get_locked_users()
    assert len(locked_users) == 0

    user_1 = user_service.lock_user(user_1)

    locked_users = user_service.get_locked_users()
    assert len(locked_users) == 1
    assert locked_users[0].id == user_1.id

    user_2 = user_service.lock_user(user_2)

    locked_users = user_service.get_locked_users()
    assert len(locked_users) == 2

    for locked_user in locked_users:
        if locked_user.id == user_1.id:
            assert locked_user.locked_at == user_1.locked_at
        elif locked_user.id == user_2.id:
            assert locked_user.locked_at == user_2.locked_at
        else:
            raise AssertionError()

    # Cleanup
    user_service.unlock_user(user_1)
    user_service.unlock_user(user_2)


def test_lock_unlocker_user(unique_user: TestUser) -> None:
    database = unique_user.repos
    user_service = UserService(database)

    # Test that the user is unlocked
    user = database.users.get_one(unique_user.user_id)
    assert user
    assert not user.locked_at

    # Test that the user is locked
    locked_user = user_service.lock_user(user)

    assert locked_user.locked_at
    assert locked_user.is_locked

    unlocked_user = user_service.unlock_user(locked_user)
    assert not unlocked_user.locked_at
    assert not unlocked_user.is_locked

    # Sanity check that the is_locked property is working
    user.locked_at = datetime.now(UTC) - timedelta(days=2)
    assert not user.is_locked


@pytest.mark.parametrize("use_task", [True, False])
def test_reset_locked_users(unique_user: TestUser, use_task: bool) -> None:
    database = unique_user.repos
    user_service = UserService(database)

    # Test that the user is unlocked
    user = database.users.get_one(unique_user.user_id)
    assert user
    assert not user.is_locked
    assert not user.locked_at

    # Test that the user is locked
    user.login_attemps = 5
    user = user_service.lock_user(user)
    assert user.is_locked
    assert user.login_attemps == 5

    # Test that the locked user is not unlocked by reset
    if use_task:
        unlocked = locked_user_reset()
    else:
        unlocked = user_service.reset_locked_users()
    user = database.users.get_one(unique_user.user_id)
    assert user
    assert unlocked == 0
    assert user.is_locked
    assert user.login_attemps == 5

    # Test that the locked user is unlocked by reset
    user.locked_at = datetime.now(UTC) - timedelta(days=2)
    database.users.update(user.id, user)
    if use_task:
        unlocked = locked_user_reset()
    else:
        unlocked = user_service.reset_locked_users()
    user = database.users.get_one(unique_user.user_id)
    assert user
    assert unlocked == 1
    assert not user.is_locked
    assert user.login_attemps == 0
