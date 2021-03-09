from datetime import date
from typing import List, Optional

from pydantic import BaseModel, validator


class MealIn(BaseModel):
    name: Optional[str]
    slug: Optional[str]
    date: Optional[date]


class MealOut(MealIn):
    image: Optional[str]
    description: Optional[str]

    class Config:
        orm_mode = True


class MealPlanBase(BaseModel):
    startDate: date
    endDate: date
    meals: List[MealIn]

    @validator("endDate")
    def endDate_after_startDate(cls, v, values, **kwargs):
        if "startDate" in values and v < values["startDate"]:
            raise ValueError("EndDate should be greater than StartDate")
        return v


class MealPlanProcessed(MealPlanBase):
    meals: list[MealOut]


class MealPlanInDB(MealPlanProcessed):
    uid: str

    class Config:
        orm_mode = True


class MealPlan(BaseModel):
    uid: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "startDate": date.today(),
                "endDate": date.today(),
                "meals": [
                    {"slug": "Packed Mac and Cheese", "date": date.today()},
                    {"slug": "Eggs and Toast", "date": date.today()},
                ],
            }
        }
