from pydantic import validator

from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema._mealie.validators import validate_locale


class SeederConfig(MealieModel):
    locale: str

    @validator("locale")
    def valid_locale(cls, v, values, **kwargs):
        if not validate_locale(v):
            raise ValueError("invalid locale")
        return v
