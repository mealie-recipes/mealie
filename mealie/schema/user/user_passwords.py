from pydantic import UUID4

from mealie.schema._mealie import MealieModel

from .user import PrivateUser


class ForgotPassword(MealieModel):
    email: str


class ValidateResetToken(MealieModel):
    token: str


class ResetPassword(ValidateResetToken):
    email: str
    password: str
    passwordConfirm: str


class SavePasswordResetToken(MealieModel):
    user_id: UUID4
    token: str


class PrivatePasswordResetToken(SavePasswordResetToken):
    user: PrivateUser

    class Config:
        orm_mode = True
