from datetime import datetime, timedelta

from mealie.repos.repository_factory import AllRepositories
from mealie.services.user_services.user_service import UserService
from tests.utils.fixture_schemas import TestUser


def test_get_locked_users(database: AllRepositories, user_tuple: list[TestUser]) -> None:
    usr_1, usr_2 = user_tuple

    # Setup
    user_service = UserService(database)

    user_1 = database.users.get_one(usr_1.user_id)
    user_2 = database.users.get_one(usr_2.user_id)

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
            assert False

    # Cleanup
    user_service.unlock_user(user_1)
    user_service.unlock_user(user_2)


def test_lock_unlocker_user(database: AllRepositories, unique_user: TestUser) -> None:
    user_service = UserService(database)

    # Test that the user is unlocked
    user = database.users.get_one(unique_user.user_id)
    assert not user.locked_at

    # Test that the user is locked
    locked_user = user_service.lock_user(user)

    assert locked_user.locked_at
    assert locked_user.is_locked

    unlocked_user = user_service.unlock_user(locked_user)
    assert not unlocked_user.locked_at
    assert not unlocked_user.is_locked

    # Sanity check that the is_locked property is working
    user.locked_at = datetime.now() - timedelta(days=2)
    assert not user.is_locked
