from mealie.db.database import Database
from mealie.schema.user import PrivateUser
from tests.utils.fixture_schemas import TestUser


def test_user_directory_deleted_on_delete(database: Database, unique_user: TestUser) -> None:
    user_dir = PrivateUser.get_directory(unique_user.user_id)
    assert user_dir.exists()
    database.users.delete(unique_user.user_id)
    assert not user_dir.exists()
