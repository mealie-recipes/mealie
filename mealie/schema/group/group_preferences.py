from enum import Enum
from typing import Any
from uuid import UUID

from pydantic import UUID4, ConfigDict, Field, field_validator

from mealie.schema._mealie import MealieModel


class GroupPreferencesPluralHandling(Enum):
    always_pluralize = "always_pluralize"
    pluralize_food_without_unit = "pluralize_food_without_unit"
    disable = "disable"


class UpdateGroupPreferences(MealieModel):
    private_group: bool = True
    plural_handling: GroupPreferencesPluralHandling = Field(default=None, validate_default=True)

    model_config = ConfigDict(use_enum_values=True)

    @field_validator("plural_handling", mode="before")
    def validate_plural_handling(v: Any) -> str:
        # We return the value as a string because Pydantic will convert it to an Enum automatically,
        # and not doing this causes issues with sqlalchemy
        if isinstance(v, Enum):
            return v.value
        elif not v:
            return GroupPreferencesPluralHandling.pluralize_food_without_unit.value
        else:
            return v


class CreateGroupPreferences(UpdateGroupPreferences):
    group_id: UUID


class ReadGroupPreferences(CreateGroupPreferences):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)
