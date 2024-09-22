from functools import cached_property

from fastapi import Query
from pydantic import UUID4

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.schema.group.group_statistics import GroupStorage
from mealie.schema.response.pagination import PaginationQuery
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

    @router.get("/members", response_model=list[UserSummary])
    def get_group_members(self, household_id: UUID4 | None = Query(None, alias="householdId")):
        """Returns all users belonging to the current group, optionally filtered by household_id"""

        query_filter = f"household_id={household_id}" if household_id else None
        private_users = self.repos.users.page_all(PaginationQuery(page=1, per_page=-1, query_filter=query_filter)).items
        return [user.cast(UserSummary) for user in private_users]

    @router.get("/preferences", response_model=ReadGroupPreferences)
    def get_group_preferences(self):
        return self.group.preferences

    @router.put("/preferences", response_model=ReadGroupPreferences)
    def update_group_preferences(self, new_pref: UpdateGroupPreferences):
        return self.repos.group_preferences.update(self.group_id, new_pref)

    @router.get("/storage", response_model=GroupStorage)
    def get_storage(self):
        return self.service.calculate_group_storage()
