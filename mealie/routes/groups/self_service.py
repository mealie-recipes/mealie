from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.schema.group.group_permissions import SetPermissions
from mealie.schema.user.user import GroupInDB, UserOut
from mealie.services.group_services.group_service import GroupSelfService

user_router = UserAPIRouter(prefix="/groups", tags=["Groups: Self Service"])


@user_router.get("/self", response_model=GroupInDB)
async def get_logged_in_user_group(g_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    """ Returns the Group Data for the Current User """
    return g_service.item


@user_router.get("/members", response_model=list[UserOut])
async def get_group_members(g_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    """ Returns the Group of user lists """
    return g_service.get_members()


@user_router.put("/permissions", response_model=UserOut)
async def set_member_permissions(
    payload: SetPermissions, g_service: GroupSelfService = Depends(GroupSelfService.manage_existing)
):
    return g_service.set_member_permissions(payload)
