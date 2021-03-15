from datetime import date
from typing import List, Optional

from db.models.mealplan import MealPlanModel
from pydantic import BaseModel, validator
from pydantic.utils import GetterDict


class MealIn(BaseModel):
    name: Optional[str]
    slug: Optional[str]
    date: Optional[date]


class MealOut(MealIn):
    image: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class MealPlanIn(BaseModel):
    group: str
    startDate: date
    endDate: date
    meals: List[MealIn]

    @validator("endDate")
    def endDate_after_startDate(v, values, config, field):
        if "startDate" in values and v < values["startDate"]:
            raise ValueError("EndDate should be greater than StartDate")
        return v


class MealPlanProcessed(MealPlanIn):
    meals: list[MealOut]


class MealPlanInDB(MealPlanProcessed):
    uid: str

    class Config:
        orm_mode = True

        @classmethod
        def getter_dict(_cls, name_orm: MealPlanModel):
            return {
                **GetterDict(name_orm),
                "group": name_orm.group.name,
            }
