from fastapi_camelcase import CamelModel

from .group_preferences import UpdateGroupPreferences


class GroupAdminUpdate(CamelModel):
    id: int
    name: str
    preferences: UpdateGroupPreferences
