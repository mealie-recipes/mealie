import random
import shutil

from mealie.assets import users as users_assets
from mealie.db.models.users import User
from mealie.schema.user.user import PrivateUser

from ._access_model import AccessModel


class UserDataAccessModel(AccessModel[PrivateUser, User]):
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
