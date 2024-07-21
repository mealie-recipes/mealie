from functools import cached_property

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from mealie.schema.group.group import GroupAdminUpdate
from mealie.schema.mapper import mapper
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.responses import ErrorResponse
from mealie.schema.user.user import GroupBase, GroupInDB, GroupPagination
from mealie.services.group_services.group_service import GroupService

from .._base import BaseAdminController, controller
from .._base.mixins import HttpRepo

router = APIRouter(prefix="/groups")


@controller(router)
class AdminGroupManagementRoutes(BaseAdminController):
    @cached_property
    def repo(self):
        if not self.user:
            raise Exception("No user is logged in.")

        return self.repos.groups

    # =======================================================================
    # CRUD Operations

    @property
    def mixins(self):
        return HttpRepo[GroupBase, GroupInDB, GroupAdminUpdate](
            self.repo,
            self.logger,
            self.registered_exceptions,
        )

    @router.get("", response_model=GroupPagination)
    def get_all(self, q: PaginationQuery = Depends(PaginationQuery)):
        response = self.repo.page_all(
            pagination=q,
            override=GroupInDB,
        )

        response.set_pagination_guides(router.url_path_for("get_all"), q.model_dump())
        return response

    @router.post("", response_model=GroupInDB, status_code=status.HTTP_201_CREATED)
    def create_one(self, data: GroupBase):
        return GroupService.create_group(self.repos, data)

    @router.get("/{item_id}", response_model=GroupInDB)
    def get_one(self, item_id: UUID4):
        return self.mixins.get_one(item_id)

    @router.put("/{item_id}", response_model=GroupInDB)
    def update_one(self, item_id: UUID4, data: GroupAdminUpdate):
        group = self.repo.get_one(item_id)

        if data.preferences:
            preferences = self.repos.group_preferences.get_one(value=item_id, key="group_id")
            preferences = mapper(data.preferences, preferences)
            group.preferences = self.repos.group_preferences.update(item_id, preferences)

        if data.name not in ["", group.name]:
            # only update the group if the name changed, since the name is the only field that can be updated
            group.name = data.name
            group = self.repo.update(item_id, group)

        return group

    @router.delete("/{item_id}", response_model=GroupInDB)
    def delete_one(self, item_id: UUID4):
        item = self.repo.get_one(item_id)

        if item and len(item.users) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorResponse.respond(message="Cannot delete group with users"),
            )

        return self.mixins.delete_one(item_id)
