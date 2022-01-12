from fastapi import HTTPException, status

from mealie.routes._base.abc_controller import BaseUserController
from mealie.routes._base.controller import controller
from mealie.routes.routers import UserAPIRouter
from mealie.schema.group.group_permissions import SetPermissions
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.schema.user.user import GroupInDB, UserOut

router = UserAPIRouter(prefix="/groups", tags=["Groups: Self Service"])


@controller(router)
class GroupSelfServiceController(BaseUserController):
    def can_manage(self):
        """Override parent method to remove `item_id` from arguments"""
        if not self.user.can_manage:
            raise HTTPException(status.HTTP_403_FORBIDDEN)

    @router.get("/preferences", response_model=ReadGroupPreferences)
    def get_group_preferences(self):
        return self.group.preferences

    @router.put("/preferences", response_model=ReadGroupPreferences)
    def update_group_preferences(self, new_pref: UpdateGroupPreferences):
        return self.repos.group_preferences.update(self.group_id, new_pref)

    @router.get("/self", response_model=GroupInDB)
    async def get_logged_in_user_group(self):
        """Returns the Group Data for the Current User"""
        return self.group

    @router.get("/members", response_model=list[UserOut])
    async def get_group_members(self):
        """Returns the Group of user lists"""
        return self.repos.users.multi_query(query_by={"group_id": self.group.id}, override_schema=UserOut)

    @router.put("/permissions", response_model=UserOut)
    async def set_member_permissions(self, permissions: SetPermissions):
        self.can_manage()

        target_user = self.repos.users.get(permissions.user_id)

        if not target_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, detail="User not found")

        if target_user.group_id != self.group_id:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="User is not a member of this group")

        target_user.can_invite = permissions.can_invite
        target_user.can_manage = permissions.can_manage
        target_user.can_organize = permissions.can_organize

        return self.repos.users.update(permissions.user_id, target_user)
