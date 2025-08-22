from enum import Enum
from uuid import UUID

from pydantic import UUID4, ConfigDict

from mealie.schema._mealie import MealieModel


class GroupPreferencesPluralHanding(Enum):
    always_pluralize = "always_pluralize"
    pluralize_food_without_unit = "pluralize_food_without_unit"
    disable = "disable"


class UpdateGroupPreferences(MealieModel):
    private_group: bool = True
    plural_handling: GroupPreferencesPluralHanding = GroupPreferencesPluralHanding.pluralize_food_without_unit


class CreateGroupPreferences(UpdateGroupPreferences):
    group_id: UUID


class ReadGroupPreferences(CreateGroupPreferences):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)
