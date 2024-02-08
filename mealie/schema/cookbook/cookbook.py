from pydantic import ConfigDict, UUID4, validator
from slugify import slugify
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary, RecipeTool
from mealie.schema.response.pagination import PaginationBase

from ...db.models.group import CookBook
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

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("public", always=True, pre=True)
    def validate_public(public: bool | None, values: dict) -> bool:  # type: ignore
        return False if public is None else public

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
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
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [joinedload(CookBook.categories), joinedload(CookBook.tags), joinedload(CookBook.tools)]


class CookBookPagination(PaginationBase):
    items: list[ReadCookBook]


class RecipeCookBook(ReadCookBook):
    group_id: UUID4
    recipes: list[RecipeSummary]
    model_config = ConfigDict(from_attributes=True)
