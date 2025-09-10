from datetime import datetime
from typing import Annotated

from pydantic import UUID4, ConfigDict, StringConstraints, field_validator
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household import Household, HouseholdToRecipe
from mealie.db.models.users.users import User
from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.household.webhook import ReadWebhook
from mealie.schema.response.pagination import PaginationBase

from .household_preferences import ReadHouseholdPreferences, UpdateHouseholdPreferences


class HouseholdRecipeBase(MealieModel):
    last_made: datetime | None = None


class HouseholdRecipeSummary(HouseholdRecipeBase):
    recipe_id: UUID4
    model_config = ConfigDict(from_attributes=True)


class HouseholdRecipeCreate(HouseholdRecipeBase):
    household_id: UUID4
    recipe_id: UUID4


class HouseholdRecipeUpdate(HouseholdRecipeBase): ...


class HouseholdRecipeOut(HouseholdRecipeCreate):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(HouseholdToRecipe.household),
        ]


class HouseholdCreate(MealieModel):
    group_id: UUID4 | None = None
    name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
    model_config = ConfigDict(from_attributes=True)


class HouseholdSave(HouseholdCreate):
    group_id: UUID4


class UpdateHousehold(HouseholdSave):
    id: UUID4
    slug: str


class UpdateHouseholdAdmin(HouseholdSave):
    id: UUID4
    preferences: UpdateHouseholdPreferences | None = None


class HouseholdSummary(UpdateHousehold):
    preferences: ReadHouseholdPreferences | None = None
    model_config = ConfigDict(from_attributes=True)


class HouseholdUserSummary(MealieModel):
    id: UUID4
    full_name: str
    model_config = ConfigDict(from_attributes=True)


class HouseholdInDB(HouseholdSummary):
    group: str
    users: list[HouseholdUserSummary] | None = None
    webhooks: list[ReadWebhook] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(Household.group),
            joinedload(Household.webhooks),
            joinedload(Household.preferences),
            selectinload(Household.users).joinedload(User.group),
            selectinload(Household.users).joinedload(User.tokens),
        ]

    @field_validator("group", mode="before")
    def convert_group_to_name(cls, v):
        if not v or isinstance(v, str):
            return v

        try:
            return v.name
        except AttributeError:
            return v


class HouseholdPagination(PaginationBase):
    items: list[HouseholdInDB]
