from uuid import UUID

from fastapi_camelcase import CamelModel
from pydantic import NoneStr


class CreateInviteToken(CamelModel):
    uses: int


class SaveInviteToken(CamelModel):
    uses_left: int
    group_id: UUID
    token: str


class ReadInviteToken(CamelModel):
    token: str
    uses_left: int
    group_id: UUID

    class Config:
        orm_mode = True


class EmailInvitation(CamelModel):
    email: str
    token: str


class EmailInitationResponse(CamelModel):
    success: bool
    error: NoneStr = None
