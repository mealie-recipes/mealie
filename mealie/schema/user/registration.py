from fastapi_camelcase import CamelModel
from pydantic import validator
from pydantic.types import constr


class CreateUserRegistration(CamelModel):
    group: str = None
    group_token: str = None
    email: constr(to_lower=True, strip_whitespace=True)
    username: constr(to_lower=True, strip_whitespace=True)
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
