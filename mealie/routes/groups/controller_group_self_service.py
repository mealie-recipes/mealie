from functools import cached_property

from fastapi import HTTPException, status

from mealie.routes._base.abc_controller import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes._base.routers import UserAPIRouter
from mealie.schema.group.group_permissions import SetPermissions
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.schema.group.group_statistics import GroupStatistics, GroupStorage
from mealie.schema.user.user import GroupInDB, UserOut
from mealie.services.group_services.group_service import GroupService

router = UserAPIRouter(prefix="/groups", tags=["Groups: Self Service"])


@controller(router)
class GroupSelfServiceController(BaseUserController):
    @cached_property
    def service(self) -> GroupService:
        return GroupService(self.group_id, self.repos)

    @router.get("/self", response_model=GroupInDB)
    def get_logged_in_user_group(self):
        """Returns the Group Data for the Current User"""
        return self.group

    @router.get("/members", response_model=list[UserOut])
    def get_group_members(self):
        """Returns the Group of user lists"""
        return self.repos.users.multi_query(query_by={"group_id": self.group.id}, override_schema=UserOut)

    @router.get("/preferences", response_model=ReadGroupPreferences)
    def get_group_preferences(self):
        return self.group.preferences

    @router.put("/preferences", response_model=ReadGroupPreferences)
    def update_group_preferences(self, new_pref: UpdateGroupPreferences):
        return self.repos.group_preferences.update(self.group_id, new_pref)

    @router.put("/permissions", response_model=UserOut)
    def set_member_permissions(self, permissions: SetPermissions):
        self.checks.can_manage()

        target_user = self.repos.users.get(permissions.user_id)

        if not target_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        if target_user.group_id != self.group_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not a member of this group")

        target_user.can_invite = permissions.can_invite
        target_user.can_manage = permissions.can_manage
        target_user.can_organize = permissions.can_organize

        return self.repos.users.update(permissions.user_id, target_user)

    @router.get("/statistics", response_model=GroupStatistics)
    def get_statistics(self):
        return self.service.calculate_statistics()

    @router.get("/storage", response_model=GroupStorage)
    def get_storage(self):
        return self.service.calculate_group_storage()
