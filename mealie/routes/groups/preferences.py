from fastapi import Depends

from mealie.routes.routers import UserAPIRouter
from mealie.schema.group.group_preferences import ReadGroupPreferences, UpdateGroupPreferences
from mealie.services.group_services.group_service import GroupSelfService

router = UserAPIRouter()


@router.put("", response_model=ReadGroupPreferences)
def update_group_preferences(
    new_pref: UpdateGroupPreferences, g_service: GroupSelfService = Depends(GroupSelfService.write_existing)
):
    return g_service.update_preferences(new_pref).preferences


@router.get("", response_model=ReadGroupPreferences)
def get_group_preferences(g_service: GroupSelfService = Depends(GroupSelfService.write_existing)):
    return g_service.item.preferences
