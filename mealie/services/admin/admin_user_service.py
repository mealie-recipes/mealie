from __future__ import annotations

from functools import cached_property

from mealie.schema.user.user import UserIn, UserOut
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import AdminHttpService
from mealie.services.events import create_user_event


class AdminUserService(
    CrudHttpMixins[UserOut, UserIn, UserIn],
    AdminHttpService[int, UserOut],
):
    event_func = create_user_event
    _schema = UserOut

    @cached_property
    def dal(self):
        return self.db.users

    def populate_item(self, id: int) -> UserOut:
        self.item = self.dal.get_one(id)
        return self.item

    def get_all(self) -> list[UserOut]:
        return self.dal.get_all()

    def create_one(self, data: UserIn) -> UserOut:
        return self._create_one(data)

    def update_one(self, data: UserOut, item_id: int = None) -> UserOut:
        return self._update_one(data, item_id)

    def delete_one(self, id: int = None) -> UserOut:
        return self._delete_one(id)
