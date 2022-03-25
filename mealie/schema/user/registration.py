from pydantic import validator
from pydantic.types import NoneStr, constr

from mealie.schema._mealie import MealieModel


class CreateUserRegistration(MealieModel):
    group: NoneStr = None
    group_token: NoneStr = None
    email: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    username: constr(to_lower=True, strip_whitespace=True)  # type: ignore
    password: str
    password_confirm: str
    advanced: bool = False
    private: bool = False

    @validator("password_confirm")
    @classmethod
    def passwords_match(cls, value, values):
        if "password" in values and value != values["password"]:
            raise ValueError("passwords do not match")
        return value

    @validator("group_token", always=True)
    @classmethod
    def group_or_token(cls, value, values):
        if bool(value) is False and bool(values["group"]) is False:
            raise ValueError("group or group_token must be provided")

        return value
