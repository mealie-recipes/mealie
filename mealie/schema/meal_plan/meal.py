import datetime

from pydantic import ConfigDict, field_validator
from pydantic_core.core_schema import ValidationInfo

from mealie.schema._mealie import MealieModel


class MealIn(MealieModel):
    slug: str | None = None
    name: str | None = None
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)


class MealDayIn(MealieModel):
    date: datetime.date | None = None
    meals: list[MealIn]
    model_config = ConfigDict(from_attributes=True)


class MealDayOut(MealDayIn):
    id: int
    model_config = ConfigDict(from_attributes=True)


class MealPlanIn(MealieModel):
    group: str
    start_date: datetime.date
    end_date: datetime.date
    plan_days: list[MealDayIn]

    @field_validator("end_date")
    def end_date_after_start_date(v, info: ValidationInfo):
        if "start_date" in info.data and v < info.data["start_date"]:
            raise ValueError("EndDate should be greater than StartDate")
        return v

    model_config = ConfigDict(from_attributes=True)


class MealPlanOut(MealPlanIn):
    id: int
    shopping_list: int | None = None
    model_config = ConfigDict(from_attributes=True)
