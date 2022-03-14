import random
import shutil
from typing import Optional

from mealie.assets import users as users_assets
from mealie.schema.user.user import PrivateUser, User

from .repository_generic import RepositoryGeneric


class RepositoryUsers(RepositoryGeneric[PrivateUser, User]):
    def update_password(self, id, password: str):
        entry = self._query_one(match_value=id)
        entry.update_password(password)
        self.session.commit()

        return self.schema.from_orm(entry)

    def create(self, user: PrivateUser):
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

    def delete(self, id: str) -> User:
        entry = super().delete(id)
        # Delete the user's directory
        shutil.rmtree(PrivateUser.get_directory(id))
        return entry

    def get_by_username(self, username: str, limit=1) -> Optional[User]:
        dbuser = self.session.query(User).filter(User.username == username).one_or_none()
        if dbuser is None:
            return None
        return self.schema.from_orm(dbuser)
