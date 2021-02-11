from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class Meal(BaseModel):
    slug: Optional[str]
    name: Optional[str]
    date: date
    dateText: str
    image: Optional[str]
    description: Optional[str]


class MealData(BaseModel):
    name: Optional[str]
    slug: str
    dateText: str


class MealPlan(BaseModel):
    uid: Optional[str]
    startDate: date
    endDate: date
    meals: List[Meal]

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
