from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from db.database import db
from pydantic import BaseModel
from sqlalchemy.orm.session import Session

from services.recipe_services import Recipe

CWD = Path(__file__).parent
THIS_WEEK = CWD.parent.joinpath("data", "meal_plan", "this_week.json")
NEXT_WEEK = CWD.parent.joinpath("data", "meal_plan", "next_week.json")
WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


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

    def process_meals(self, session: Session):
        meals = []
        for x, meal in enumerate(self.meals):

            try:
                recipe = Recipe.get_by_slug(session, meal.slug)

                meal_data = {
                    "slug": recipe.slug,
                    "name": recipe.name,
                    "date": self.startDate + timedelta(days=x),
                    "dateText": meal.dateText,
                    "image": recipe.image,
                    "description": recipe.description,
                }
            except:
                meal_data = {
                    "date": self.startDate + timedelta(days=x),
                    "dateText": meal.dateText,
                }

            meals.append(Meal(**meal_data))

        self.meals = meals

    def save_to_db(self, session: Session):
        db.meals.save_new(session, self.dict())

    @staticmethod
    def get_all(session: Session) -> List:

        all_meals = [
            MealPlan(**x) for x in db.meals.get_all(session, order_by="startDate")
        ]

        return all_meals

    def update(self, session, uid):
        db.meals.update(session, uid, self.dict())

    @staticmethod
    def delete(session, uid):
        db.meals.delete(session, uid)

    @staticmethod
    def today(session: Session) -> str:
        """ Returns the meal slug for Today """
        meal_plan = db.meals.get_all(session, limit=1, order_by="startDate")

        meal_docs = [Meal(**meal) for meal in meal_plan["meals"]]

        for meal in meal_docs:
            if meal.date == date.today():
                return meal.slug

        return "No Meal Today"

    @staticmethod
    def this_week(session: Session):
        meal_plan = db.meals.get_all(session, limit=1, order_by="startDate")

        return meal_plan
