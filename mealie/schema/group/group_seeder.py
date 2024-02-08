from pydantic import validator

from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema._mealie.validators import validate_locale


class SeederConfig(MealieModel):
    locale: str

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("locale")
    def valid_locale(cls, v, values, **kwargs):
        if not validate_locale(v):
            raise ValueError("invalid locale")
        return v
