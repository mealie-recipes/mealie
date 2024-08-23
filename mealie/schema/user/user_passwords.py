from pydantic import UUID4, ConfigDict
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
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            selectinload(PasswordResetModel.user).joinedload(User.group),
            selectinload(PasswordResetModel.user).joinedload(User.household),
            selectinload(PasswordResetModel.user).joinedload(User.tokens),
        ]
