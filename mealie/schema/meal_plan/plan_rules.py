import datetime
from enum import Enum

from pydantic import UUID4

from mealie.schema._mealie import MealieModel


class Category(MealieModel):
    id: UUID4
    name: str
    slug: str

    class Config:
        orm_mode = True


class Tag(Category):
    class Config:
        orm_mode = True


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
    categories: list[Category] = []
    tags: list[Tag] = []


class PlanRulesSave(PlanRulesCreate):
    group_id: UUID4


class PlanRulesOut(PlanRulesSave):
    id: UUID4

    class Config:
        orm_mode = True
