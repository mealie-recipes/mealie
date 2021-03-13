from fastapi_camelcase import CamelModel


class SignUpIn(CamelModel):
    name: str
    admin: bool


class SignUpToken(SignUpIn):
    token: str


class SignUpOut(SignUpToken):
    id: int

    class Config:
        orm_mode = True
