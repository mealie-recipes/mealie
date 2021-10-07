from mealie.db.models.users import User
from mealie.schema.user.user import PrivateUser

from ._access_model import AccessModel


class UserDataAccessModel(AccessModel[PrivateUser, User]):
    def update_password(self, id, password: str):
        entry = self._query_one(match_value=id)
        entry.update_password(password)
        self.session.commit()

        return self.schema.from_orm(entry)
