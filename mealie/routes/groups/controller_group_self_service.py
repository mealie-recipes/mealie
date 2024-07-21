from functools import cached_property

from mealie.routes._base.base_controllers import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.schema.group.group_statistics import GroupStorage
from mealie.schema.user.user import GroupSummary
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

    @router.get("/preferences", response_model=ReadGroupPreferences)
    def get_group_preferences(self):
        return self.group.preferences

    @router.put("/preferences", response_model=ReadGroupPreferences)
    def update_group_preferences(self, new_pref: UpdateGroupPreferences):
        return self.repos.group_preferences.update(self.group_id, new_pref)

    @router.get("/storage", response_model=GroupStorage)
    def get_storage(self):
        return self.service.calculate_group_storage()
