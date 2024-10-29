import datetime
from enum import Enum
from typing import Annotated

import sqlalchemy as sa
from pydantic import UUID4, ConfigDict, Field, ValidationInfo, field_validator

from mealie.core.root_logger import get_logger
from mealie.db.models.recipe import RecipeModel
from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase
from mealie.schema.response.query_filter import QueryFilterBuilder, QueryFilterJSON

logger = get_logger()


class PlanRulesDay(str, Enum):
    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"
    unset = "unset"

    @staticmethod
    def from_date(date: datetime.date):
        """Returns the enum value for the date passed in"""
        try:
            return PlanRulesDay[(date.strftime("%A").lower())]
        except KeyError:
            return PlanRulesDay.unset


class PlanRulesType(str, Enum):
    breakfast = "breakfast"
    lunch = "lunch"
    dinner = "dinner"
    side = "side"
    unset = "unset"


class PlanRulesCreate(MealieModel):
    day: PlanRulesDay = PlanRulesDay.unset
    entry_type: PlanRulesType = PlanRulesType.unset
    query_filter_string: str = ""

    @field_validator("query_filter_string")
    def validate_query_filter_string(cls, value: str) -> str:
        # The query filter builder does additional validations while building the
        # database query, so we make sure constructing the query is successful
        builder = QueryFilterBuilder(value)

        try:
            builder.filter_query(sa.select(RecipeModel), RecipeModel)
        except Exception as e:
            raise ValueError("Invalid query filter string") from e

        return value


class PlanRulesSave(PlanRulesCreate):
    group_id: UUID4
    household_id: UUID4


class PlanRulesOut(PlanRulesSave):
    id: UUID4
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


class PlanRulesPagination(PaginationBase):
    items: list[PlanRulesOut]
