import datetime
from enum import Enum

from pydantic import UUID4, ConfigDict
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.household import GroupMealPlanRules, Household
from mealie.db.models.recipe import Category, Tag
from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class BasePlanRuleFilter(MealieModel):
    id: UUID4
    name: str
    slug: str


class PlanCategory(BasePlanRuleFilter):
    model_config = ConfigDict(from_attributes=True)


class PlanTag(BasePlanRuleFilter):
    model_config = ConfigDict(from_attributes=True)


class PlanHousehold(BasePlanRuleFilter):
    model_config = ConfigDict(from_attributes=True)


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
    categories: list[PlanCategory] = []
    tags: list[PlanTag] = []
    households: list[PlanHousehold] = []


class PlanRulesSave(PlanRulesCreate):
    group_id: UUID4
    household_id: UUID4


class PlanRulesOut(PlanRulesSave):
    id: UUID4
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [
            joinedload(GroupMealPlanRules.categories).load_only(
                Category.id,
                Category.name,
                Category.slug,
            ),
            joinedload(GroupMealPlanRules.tags).load_only(
                Tag.id,
                Tag.name,
                Tag.slug,
            ),
            joinedload(GroupMealPlanRules.households).load_only(
                Household.id,
                Household.name,
                Household.slug,
            ),
        ]


class PlanRulesPagination(PaginationBase):
    items: list[PlanRulesOut]
