from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.schema.user.user import GroupInDB
from mealie.services.group.group_service import GroupSelfService

user_router = UserAPIRouter(prefix="/groups/self", tags=["Groups: Self Service"])


@user_router.get("", response_model=GroupInDB)
async def get_logged_in_user_group(g_self_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    """ Returns the Group Data for the Current User """

    return g_self_service.item
