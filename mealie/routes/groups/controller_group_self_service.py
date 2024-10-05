from functools import cached_property
from uuid import UUID

from fastapi import Depends, HTTPException
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.schema.group.group_statistics import GroupStorage
from mealie.schema.response.pagination import PaginationBase, PaginationQuery
from mealie.schema.user.user import GroupSummary, UserSummary
from mealie.services.group_services.group_service import GroupService

router = UserAPIRouter(prefix="/groups", tags=["Groups: Self Service"])


@controller(router)
class GroupSelfServiceController(BaseUserController):
    @cached_property
    def service(self) -> GroupService:
        return GroupService(self.group_id, self.repos)

    @router.get("/self", response_model=GroupSummary)
    def get_logged_in_user_group(self):
        """Returns the Group Data for the Current User"""
        return self.group.cast(GroupSummary)

    @router.get("/members", response_model=PaginationBase[UserSummary])
    def get_group_members(self, q: PaginationQuery = Depends()):
        """Returns all users belonging to the current group"""

        response = self.repos.users.page_all(q, override=UserSummary)
        response.set_pagination_guides(router.url_path_for("get_group_members"), q.model_dump())
        return response

    @router.get("/members/{username_or_id}", response_model=UserSummary)
    def get_group_member(self, username_or_id: str | UUID4):
        """Returns a single user belonging to the current group"""

        try:
            UUID(username_or_id)
            key = "id"
        except ValueError:
            key = "username"

        private_user = self.repos.users.get_one(username_or_id, key)
        if not private_user:
            raise HTTPException(status_code=404, detail="User Not Found")

        return private_user.cast(UserSummary)

    @router.get("/preferences", response_model=ReadGroupPreferences)
    def get_group_preferences(self):
        return self.group.preferences

    @router.put("/preferences", response_model=ReadGroupPreferences)
    def update_group_preferences(self, new_pref: UpdateGroupPreferences):
        return self.repos.group_preferences.update(self.group_id, new_pref)

    @router.get("/storage", response_model=GroupStorage)
    def get_storage(self):
        return self.service.calculate_group_storage()
