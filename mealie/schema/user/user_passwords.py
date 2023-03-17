from pydantic import UUID4
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.schema._mealie import MealieModel

from ...db.models.users import PasswordResetModel, User
from .user import PrivateUser


class ForgotPassword(MealieModel):
    email: str


class PasswordResetToken(MealieModel):
    token: str


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

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(PasswordResetModel.user).joinedload(User.group),
            selectinload(PasswordResetModel.user).joinedload(User.favorite_recipes),
            selectinload(PasswordResetModel.user).joinedload(User.tokens),
        ]
