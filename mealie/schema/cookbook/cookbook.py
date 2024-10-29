from typing import Annotated

import sqlalchemy as sa
from pydantic import UUID4, ConfigDict, Field, ValidationInfo, field_validator
from slugify import slugify

from mealie.core.root_logger import get_logger
from mealie.db.models.recipe import RecipeModel
from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase
from mealie.schema.response.query_filter import QueryFilterBuilder, QueryFilterJSON

logger = get_logger()


class CreateCookBook(MealieModel):
    name: str
    description: str = ""
    slug: Annotated[str | None, Field(validate_default=True)] = None
    position: int = 1
    public: Annotated[bool, Field(validate_default=True)] = False
    query_filter_string: str = ""

    @field_validator("public", mode="before")
    def validate_public(public: bool | None) -> bool:
        return False if public is None else public

    @field_validator("name")
    def validate_name(name: str) -> str:
        name = name.strip()

        # we calculate the slug later leveraging the database,
        # but we still need to validate the name can be slugified
        possible_slug = slugify(name)
        if not (name and possible_slug):
            raise ValueError("Name cannot be empty")

        return name

    @field_validator("query_filter_string")
    def validate_query_filter_string(value: str) -> str:
        # The query filter builder does additional validations while building the
        # database query, so we make sure constructing the query is successful
        builder = QueryFilterBuilder(value)

        try:
            builder.filter_query(sa.select(RecipeModel), RecipeModel)
        except Exception as e:
            raise ValueError("Invalid query filter string") from e

        return value


class SaveCookBook(CreateCookBook):
    group_id: UUID4
    household_id: UUID4


class UpdateCookBook(SaveCookBook):
    id: UUID4


class ReadCookBook(UpdateCookBook):
    query_filter: Annotated[QueryFilterJSON, Field(validate_default=True)] = None  # type: ignore

    model_config = ConfigDict(from_attributes=True)

    @field_validator("query_filter_string")
    def validate_query_filter_string(value: str) -> str:
        # Skip validation since we are not updating the query filter string
        return value

    @field_validator("query_filter", mode="before")
    def validate_query_filter(cls, _, info: ValidationInfo) -> QueryFilterJSON:
        try:
            query_filter_string: str = info.data.get("query_filter_string") or ""
            builder = QueryFilterBuilder(query_filter_string)
            return builder.as_json_model()
        except Exception:
            logger.exception(f"Invalid query filter string: {query_filter_string}")
            return QueryFilterJSON()


class CookBookPagination(PaginationBase):
    items: list[ReadCookBook]


class RecipeCookBook(ReadCookBook):
    group_id: UUID4
    household_id: UUID4
    recipes: list[RecipeSummary]
    model_config = ConfigDict(from_attributes=True)
