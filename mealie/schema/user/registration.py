from pydantic import StringConstraints, validator
from pydantic.types import NoneStr, constr

from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.validators import validate_locale
from typing_extensions import Annotated


class CreateUserRegistration(MealieModel):
    group: NoneStr = None
    group_token: NoneStr = None
    email: Annotated[str, StringConstraints(to_lower=True, strip_whitespace=True)]  # type: ignore
    username: Annotated[str, StringConstraints(to_lower=True, strip_whitespace=True)]  # type: ignore
    password: str
    password_confirm: str
    advanced: bool = False
    private: bool = False

    seed_data: bool = False
    locale: str = "en-US"

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("locale")
    def valid_locale(cls, v, values, **kwargs):
        if not validate_locale(v):
            raise ValueError("invalid locale")
        return v

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("password_confirm")
    @classmethod
    def passwords_match(cls, value, values):
        if "password" in values and value != values["password"]:
            raise ValueError("passwords do not match")
        return value

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("group_token", always=True)
    @classmethod
    def group_or_token(cls, value, values):
        if not bool(value) and not bool(values["group"]):
            raise ValueError("group or group_token must be provided")

        return value
