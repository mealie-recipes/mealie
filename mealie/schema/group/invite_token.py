from uuid import UUID

from pydantic import NoneStr

from mealie.schema._mealie import MealieModel


class CreateInviteToken(MealieModel):
    uses: int


class SaveInviteToken(MealieModel):
    uses_left: int
    group_id: UUID
    token: str


class ReadInviteToken(MealieModel):
    token: str
    uses_left: int
    group_id: UUID

    class Config:
        orm_mode = True


class EmailInvitation(MealieModel):
    email: str
    token: str


class EmailInitationResponse(MealieModel):
    success: bool
    error: NoneStr = None
