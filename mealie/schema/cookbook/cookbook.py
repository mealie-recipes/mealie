from fastapi_camelcase import CamelModel
from pydantic import validator
from slugify import slugify

from ..recipe.recipe_category import CategoryBase


class CreateCookBook(CamelModel):
    name: str
    description: str = ""
    slug: str = None
    position: int = 1
    categories: list[CategoryBase] = []

    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):
        name: str = values["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug


class UpdateCookBook(CreateCookBook):
    id: int


class SaveCookBook(CreateCookBook):
    group_id: int


class ReadCookBook(UpdateCookBook):
    group_id: int
    categories: list[CategoryBase] = []

    class Config:
        orm_mode = True
