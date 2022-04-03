from pydantic import UUID4, validator
from slugify import slugify

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary, RecipeTool

from ..recipe.recipe_category import CategoryBase, TagBase


class CreateCookBook(MealieModel):
    name: str
    description: str = ""
    slug: str | None = None
    position: int = 1
    public: bool = False
    categories: list[CategoryBase] = []
    tags: list[TagBase] = []
    tools: list[RecipeTool] = []
    require_all_categories: bool = True
    require_all_tags: bool = True
    require_all_tools: bool = True

    @validator("public", always=True, pre=True)
    def validate_public(public: bool | None, values: dict) -> bool:  # type: ignore
        return False if public is None else public

    @validator("slug", always=True, pre=True)
    def validate_slug(slug: str, values):  # type: ignore
        name: str = values["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug


class SaveCookBook(CreateCookBook):
    group_id: UUID4


class UpdateCookBook(SaveCookBook):
    id: UUID4


class ReadCookBook(UpdateCookBook):
    group_id: UUID4
    categories: list[CategoryBase] = []

    class Config:
        orm_mode = True


class RecipeCookBook(ReadCookBook):
    group_id: UUID4
    recipes: list[RecipeSummary]

    class Config:
        orm_mode = True
