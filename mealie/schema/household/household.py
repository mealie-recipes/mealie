from typing import Annotated

from pydantic import UUID4, ConfigDict, StringConstraints

from mealie.schema._mealie.mealie_model import MealieModel

from .household_preferences import ReadHouseholdPreferences


class HouseholdBase(MealieModel):
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    model_config = ConfigDict(from_attributes=True)


class UpdateHousehold(HouseholdBase):
    id: UUID4
    group_id: UUID4
    slug: str


class HouseholdOut(UpdateHousehold):
    model_config = ConfigDict(from_attributes=True)
    preferences: ReadHouseholdPreferences | None = None
