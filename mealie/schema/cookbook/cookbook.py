from typing import Annotated

from pydantic import UUID4, ConfigDict, Field, ValidationInfo, field_validator

from mealie.schema._mealie import MealieModel
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.response.pagination import PaginationBase
from mealie.schema.response.query_filter import QueryFilterBuilder, QueryFilterJSON


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


class SaveCookBook(CreateCookBook):
    group_id: UUID4
    household_id: UUID4


class UpdateCookBook(SaveCookBook):
    id: UUID4


class ReadCookBook(UpdateCookBook):
    query_filter: Annotated[QueryFilterJSON, Field(validate_default=True)] = None  # type: ignore

    model_config = ConfigDict(from_attributes=True)

    @field_validator("query_filter", mode="before")
    def validate_query_filter(cls, _, info: ValidationInfo) -> QueryFilterJSON:
        query_filter_string: str = info.data.get("query_filter_string") or ""
        builder = QueryFilterBuilder(query_filter_string)
        return builder.as_json_model()


class CookBookPagination(PaginationBase):
    items: list[ReadCookBook]


class RecipeCookBook(ReadCookBook):
    group_id: UUID4
    household_id: UUID4
    recipes: list[RecipeSummary]
    model_config = ConfigDict(from_attributes=True)
