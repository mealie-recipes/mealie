from __future__ import annotations

from functools import cached_property

from fastapi import HTTPException, status
from pydantic import UUID4

from mealie.schema.group.group import GroupAdminUpdate
from mealie.schema.mapper import mapper
from mealie.schema.response import ErrorResponse
from mealie.schema.user.user import GroupBase, GroupInDB
from mealie.services._base_http_service.crud_http_mixins import CrudHttpMixins
from mealie.services._base_http_service.http_services import AdminHttpService
from mealie.services.events import create_group_event
from mealie.services.group_services.group_utils import create_new_group


class AdminGroupService(
    CrudHttpMixins[GroupBase, GroupInDB, GroupAdminUpdate],
    AdminHttpService[UUID4, GroupInDB],
):
    event_func = create_group_event
    _schema = GroupInDB

    @cached_property
    def dal(self):
        return self.db.groups

    def populate_item(self, id: UUID4) -> GroupInDB:
        self.item = self.dal.get_one(id)
        return self.item

    def get_all(self) -> list[GroupInDB]:
        return self.dal.get_all()

    def create_one(self, data: GroupBase) -> GroupInDB:
        return create_new_group(self.db, data)

    def update_one(self, data: GroupAdminUpdate, item_id: UUID4 = None) -> GroupInDB:
        target_id = item_id or data.id

        if data.preferences:
            preferences = self.db.group_preferences.get_one(value=target_id, key="group_id")
            preferences = mapper(data.preferences, preferences)
            self.item.preferences = self.db.group_preferences.update(target_id, preferences)

        if data.name not in ["", self.item.name]:
            self.item.name = data.name
            self.item = self.dal.update(target_id, self.item)

        return self.item

    def delete_one(self, id: UUID4 = None) -> GroupInDB:
        target_id = id or self.item.id

        if len(self.item.users) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse(message="Cannot delete group with users").dict(),
            )

        return self._delete_one(target_id)
