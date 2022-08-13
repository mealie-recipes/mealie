import random
import shutil

from pydantic import UUID4

from mealie.assets import users as users_assets
from mealie.schema.user.user import PrivateUser, User

from .repository_generic import RepositoryGeneric


class RepositoryUsers(RepositoryGeneric[PrivateUser, User]):
    def update_password(self, id, password: str):
        entry = self._query_one(match_value=id)
        entry.update_password(password)
        self.session.commit()

        return self.schema.from_orm(entry)

    def create(self, user: PrivateUser | dict):  # type: ignore
        new_user = super().create(user)

        # Select Random Image
        all_images = [
            users_assets.img_random_1,
            users_assets.img_random_2,
            users_assets.img_random_3,
        ]
        random_image = random.choice(all_images)
        shutil.copy(random_image, new_user.directory() / "profile.webp")

        return new_user

    def delete(self, value: str | UUID4, match_key: str | None = None) -> User:
        entry = super().delete(value, match_key)
        # Delete the user's directory
        shutil.rmtree(PrivateUser.get_directory(value))
        return entry  # type: ignore

    def get_by_username(self, username: str) -> PrivateUser | None:
        dbuser = self.session.query(User).filter(User.username == username).one_or_none()
        return None if dbuser is None else self.schema.from_orm(dbuser)

    def get_locked_users(self) -> list[PrivateUser]:
        results = self.session.query(User).filter(User.locked_at != None).all()  # noqa E711
        return [self.schema.from_orm(x) for x in results]
