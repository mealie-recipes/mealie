from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.schema.user.user import GroupInDB
from mealie.services.group_services.group_service import GroupSelfService

user_router = UserAPIRouter(prefix="/groups", tags=["Groups: Self Service"])


@user_router.get("/self", response_model=GroupInDB)
async def get_logged_in_user_group(g_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    """ Returns the Group Data for the Current User """

    return g_service.item


@user_router.put("/preferences", response_model=ReadGroupPreferences)
def update_group_preferences(
    new_pref: UpdateGroupPreferences, g_service: GroupSelfService = Depends(GroupSelfService.write_existing)
):
    return g_service.update_preferences(new_pref).preferences


@user_router.get("/preferences", response_model=ReadGroupPreferences)
def get_group_preferences(g_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    return g_service.item.preferences
