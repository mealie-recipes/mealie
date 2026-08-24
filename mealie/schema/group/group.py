from pydantic import UUID4

from mealie.schema._mealie import MealieModel

from .ai_providers import AIProviderSettingsUpdate
from .group_preferences import UpdateGroupPreferences


class GroupAdminUpdate(MealieModel):
    id: UUID4
    name: str
    preferences: UpdateGroupPreferences | None = None
    ai_provider_settings: AIProviderSettingsUpdate | None = None
