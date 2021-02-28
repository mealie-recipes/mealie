from fastapi_camelcase import CamelModel


class SignUpIn(CamelModel):
    name: str


class SignUpToken(SignUpIn):
    token: str


class SignUpOut(SignUpToken):
    id: int
