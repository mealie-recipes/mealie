from uuid import UUID

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import MealieOutModel


class GroupPreferencesUpdate(MealieModel):
    private_group: bool = True
    show_announcements: bool = True


class GroupPreferencesCreate(GroupPreferencesUpdate):
    group_id: UUID


class GroupPreferencesOut(GroupPreferencesCreate, MealieOutModel):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)
