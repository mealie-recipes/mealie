from datetime import date

from pydantic import validator

from mealie.schema._mealie import MealieModel


class MealIn(MealieModel):
    slug: str | None
    name: str | None
    description: str | None

    class Config:
        orm_mode = True


class MealDayIn(MealieModel):
    date: date | None
    meals: list[MealIn]

    class Config:
        orm_mode = True


class MealDayOut(MealDayIn):
    id: int

    class Config:
        orm_mode = True


class MealPlanIn(MealieModel):
    group: str
    start_date: date
    end_date: date
    plan_days: list[MealDayIn]

    @validator("end_date")
    def end_date_after_start_date(v, values, config, field):
        if "start_date" in values and v < values["start_date"]:
            raise ValueError("EndDate should be greater than StartDate")
        return v

    class Config:
        orm_mode = True


class MealPlanOut(MealPlanIn):
    id: int
    shopping_list: int | None

    class Config:
        orm_mode = True
