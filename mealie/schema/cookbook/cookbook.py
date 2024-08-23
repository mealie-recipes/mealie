from typing import Annotated

from pydantic import UUID4, ConfigDict, Field, field_validator
from pydantic_core.core_schema import ValidationInfo
from slugify import slugify
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary, RecipeTool
from mealie.schema.response.pagination import PaginationBase

from ...db.models.household import CookBook
from ..recipe.recipe_category import CategoryBase, TagBase


class CreateCookBook(MealieModel):
    name: str
    description: str = ""
    slug: Annotated[str | None, Field(validate_default=True)] = None
    position: int = 1
    public: Annotated[bool, Field(validate_default=True)] = False
    categories: list[CategoryBase] = []
    tags: list[TagBase] = []
    tools: list[RecipeTool] = []
    require_all_categories: bool = True
    require_all_tags: bool = True
    require_all_tools: bool = True

    @field_validator("public", mode="before")
    def validate_public(public: bool | None) -> bool:
        return False if public is None else public

    @field_validator("slug", mode="before")
    def validate_slug(slug: str, info: ValidationInfo):
        name: str = info.data["name"]
        calc_slug: str = slugify(name)

        if slug != calc_slug:
            slug = calc_slug

        return slug


class SaveCookBook(CreateCookBook):
    group_id: UUID4
    household_id: UUID4


class UpdateCookBook(SaveCookBook):
    id: UUID4


class ReadCookBook(UpdateCookBook):
    group_id: UUID4
    household_id: UUID4
    categories: list[CategoryBase] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(CookBook.categories), joinedload(CookBook.tags), joinedload(CookBook.tools)]


class CookBookPagination(PaginationBase):
    items: list[ReadCookBook]


class RecipeCookBook(ReadCookBook):
    group_id: UUID4
    household_id: UUID4
    recipes: list[RecipeSummary]
    model_config = ConfigDict(from_attributes=True)
