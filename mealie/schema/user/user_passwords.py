from fastapi_camelcase import CamelModel

from .user import PrivateUser


class ForgotPassword(CamelModel):
    email: str


class ValidateResetToken(CamelModel):
    token: str


class ResetPassword(ValidateResetToken):
    email: str
    password: str
    passwordConfirm: str


class SavePasswordResetToken(CamelModel):
    user_id: int
    token: str


class PrivatePasswordResetToken(SavePasswordResetToken):
    user: PrivateUser

    class Config:
        orm_mode = True
