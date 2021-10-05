from fastapi_camelcase import CamelModel


class CreateInviteToken(CamelModel):
    uses: int


class SaveInviteToken(CamelModel):
    uses_left: int
    group_id: int
    token: str


class ReadInviteToken(CamelModel):
    token: str
    uses_left: int
    group_id: int

    class Config:
        orm_mode = True


class EmailInvitation(CamelModel):
    email: str
    token: str


class EmailInitationResponse(CamelModel):
    success: bool
    error: str = None
