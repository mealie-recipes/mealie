from uuid import UUID

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel


class UpdateGroupPreferences(MealieModel):
    private_group: bool = True


class CreateGroupPreferences(UpdateGroupPreferences):
    group_id: UUID


class ReadGroupPreferences(CreateGroupPreferences):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)
