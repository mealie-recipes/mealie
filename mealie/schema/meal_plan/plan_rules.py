import datetime
from enum import Enum

from pydantic import UUID4, ConfigDict, field_validator

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase
from mealie.schema.response.query_filter import QueryFilterBuilder, QueryFilterJSON


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
    query_filter_string: str


class PlanRulesSave(PlanRulesCreate):
    group_id: UUID4
    household_id: UUID4


class PlanRulesOut(PlanRulesSave):
    id: UUID4
    query_filter: QueryFilterJSON

    model_config = ConfigDict(from_attributes=True)

    @field_validator("query_filter_string", mode="before")
    def validate_query_filter(_, values) -> QueryFilterJSON:
        query_filter_string: str = values.get("query_filter_string") or ""
        builder = QueryFilterBuilder(query_filter_string)
        return builder.as_json_model()


class PlanRulesPagination(PaginationBase):
    items: list[PlanRulesOut]
