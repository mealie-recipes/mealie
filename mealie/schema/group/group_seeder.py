from pydantic import field_validator

from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema._mealie.validators import validate_locale


class SeederConfig(MealieModel):
    locale: str

    @field_validator("locale")
    def valid_locale(cls, v):
        if not validate_locale(v):
            raise ValueError("invalid locale")
        return v
