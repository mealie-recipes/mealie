from pydantic import ConfigDict, validator
from slugify import slugify

from mealie.schema._mealie import MealieModel

from ..recipe.recipe_category import RecipeCategoryResponse


class CustomPageBase(MealieModel):
    name: str
    slug: str | None
    position: int
    categories: list[RecipeCategoryResponse] = []
    model_config = ConfigDict(from_attributes=True)

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):
        name: str = values["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug


class CustomPageOut(CustomPageBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
