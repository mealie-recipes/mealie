from fastapi_camelcase import CamelModel
from pydantic import UUID4

from .group_preferences import UpdateGroupPreferences


class GroupAdminUpdate(CamelModel):
    id: UUID4
    name: str
    preferences: UpdateGroupPreferences
