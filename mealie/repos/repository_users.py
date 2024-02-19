import random
import shutil

from pydantic import UUID4
from sqlalchemy import select

from mealie.assets import users as users_assets
from mealie.core.config import get_app_settings
from mealie.schema.user.user import PrivateUser

from ..db.models.users import User
from .repository_generic import RepositoryGeneric

settings = get_app_settings()


class RepositoryUsers(RepositoryGeneric[PrivateUser, User]):
    def update_password(self, id, password: str):
        entry = self._query_one(match_value=id)
        if settings.IS_DEMO:
            user_to_update = self.schema.model_validate(entry)
            if user_to_update.is_default_user:
                # do not update the default user in demo mode
                return user_to_update

        entry.update_password(password)
        self.session.commit()

        return self.schema.model_validate(entry)

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

    def update(self, match_value: str | int | UUID4, new_data: dict | PrivateUser) -> PrivateUser:
        if settings.IS_DEMO:
            user_to_update = self.get_one(match_value)
            if user_to_update and user_to_update.is_default_user:
                # do not update the default user in demo mode
                return user_to_update

        return super().update(match_value, new_data)

    def delete(self, value: str | UUID4, match_key: str | None = None) -> User:
        if settings.IS_DEMO:
            user_to_delete = self.get_one(value, match_key)
            if user_to_delete and user_to_delete.is_default_user:
                # do not update the default user in demo mode
                return user_to_delete

        entry = super().delete(value, match_key)
        # Delete the user's directory
        shutil.rmtree(PrivateUser.get_directory(value))
        return entry

    def get_by_username(self, username: str) -> PrivateUser | None:
        stmt = select(User).filter(User.username == username)
        dbuser = self.session.execute(stmt).scalars().one_or_none()
        return None if dbuser is None else self.schema.model_validate(dbuser)

    def get_locked_users(self) -> list[PrivateUser]:
        stmt = select(User).filter(User.locked_at != None)  # noqa E711
        results = self.session.execute(stmt).scalars().all()
        return [self.schema.model_validate(x) for x in results]
