from fastapi import HTTPException, status

from mealie.core.root_logger import get_logger
from mealie.core.security import hash_password, verify_password
from mealie.schema.user.user import ChangePassword, PrivateUser
from mealie.services._base_http_service.http_services import UserHttpService
from mealie.services.events import create_user_event

logger = get_logger(module=__name__)


class UserService(UserHttpService[int, str]):
    event_func = create_user_event
    acting_user: PrivateUser = None

    def assert_existing(self, id) -> PrivateUser:
        self._populate_target_user(id)
        self._assert_user_change_allowed()
        return self.target_user

    def _assert_user_change_allowed(self) -> None:
        if self.acting_user.id != self.target_user.id and not self.acting_user.admin:
            # only admins can edit other users
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="NOT_AN_ADMIN")

    def _populate_target_user(self, id: int = None):
        if id:
            self.target_user = self.db.users.get(self.session, id)
            if not self.target_user:
                raise HTTPException(status.HTTP_404_NOT_FOUND)
        else:
            self.target_user = self.acting_user

    def change_password(self, password_change: ChangePassword) -> PrivateUser:
        """"""
        if not verify_password(password_change.current_password, self.target_user.password):
            raise HTTPException(status.HTTP_400_BAD_REQUEST)

        self.target_user.password = hash_password(password_change.new_password)

        return self.db.users.update_password(self.session, self.target_user.id, self.target_user.password)
