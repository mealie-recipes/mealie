from mealie.db.models.users import User
from mealie.schema.user.user import PrivateUser

from ._base_access_model import BaseAccessModel


class UserDataAccessModel(BaseAccessModel[PrivateUser, User]):
    def update_password(self, session, id, password: str):
        entry = self._query_one(session=session, match_value=id)
        entry.update_password(password)
        session.commit()

        return self.schema.from_orm(entry)
