from uuid import UUID

from pydantic import ConfigDict

from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import MealieOutModel


class InviteTokenCreate(MealieModel):
    uses: int
    group_id: UUID | None = None
    household_id: UUID | None = None


class InviteTokenSave(MealieModel):
    uses_left: int
    group_id: UUID
    household_id: UUID
    token: str


class InviteTokenOut(MealieOutModel):
    token: str
    uses_left: int
    group_id: UUID
    household_id: UUID
    model_config = ConfigDict(from_attributes=True)


class EmailInvitation(MealieModel):
    email: str
    token: str


class EmailInvitationResponse(MealieModel):
    success: bool
    error: str | None = None
