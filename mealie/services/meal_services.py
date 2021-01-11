import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from db.db_setup import db
from db.mongo.meal_models import MealDocument
from pydantic import BaseModel

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

    def process_meals(self):
        meals = []
        for x, meal in enumerate(self.meals):

            try:
                recipe = Recipe.get_by_slug(meal.slug)

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

    def save_to_db(self):

        meal_docs = []
        for meal in self.meals:
            meal = meal.dict()
            meal_doc = MealDocument(**meal)
            meal_docs.append(meal_doc)

        self.meals = meal_docs
        db.meals.save_new(self.dict())

    @staticmethod
    def get_all() -> List:

        all_meals = [MealPlan(**x) for x in db.meals.get_all(order_by="startDate")]

        return all_meals

    def update(self, uid):

        meal_docs = []
        for meal in self.meals:
            meal = meal.dict()
            meal_doc = MealDocument(**meal)
            meal_docs.append(meal_doc)

        db.meals.update(uid, meal_docs)

    @staticmethod
    def delete(uid):
        db.meals.delete(uid)

    @staticmethod
    def today() -> str:
        """ Returns the meal slug for Today """
        meal_plan = db.meals.get_all(limit=1, order_by="startDate")

        meal_docs = []
        for meal in meal_plan["meals"]:
            print(meal)
            meal_doc = Meal(**meal)
            meal_docs.append(meal_doc)

        for meal in meal_docs:
            if meal.date == date.today():
                return meal.slug

        return "No Meal Today"

    @staticmethod
    def this_week():
        meal_plan = db.meals.get_all(limit=1, order_by="startDate")

        return meal_plan
