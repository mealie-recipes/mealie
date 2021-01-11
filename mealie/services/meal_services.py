import json
from datetime import date, timedelta
from pathlib import Path
from typing import List, Optional

from db.mongo.meal_models import MealDocument, MealPlanDocument
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

        meal_plan = MealPlanDocument(**self.dict())

        meal_plan.save()

    @staticmethod
    def get_all() -> List:
        all_meals = []
        for plan in MealPlanDocument.objects.order_by("startDate"):
            all_meals.append(MealPlan._unpack_doc(plan))

        print(all_meals)
        return all_meals

    def update(self, uid):
        document = MealPlanDocument.objects.get(uid=uid)

        meal_docs = []
        for meal in self.meals:
            meal = meal.dict()
            meal_doc = MealDocument(**meal)
            meal_docs.append(meal_doc)

        self.meals = meal_docs
        if document:
            document.update(set__meals=self.meals)
            document.save()

    @staticmethod
    def delete(uid):
        document = MealPlanDocument.objects.get(uid=uid)

        if document:
            document.delete()

    @staticmethod
    def _unpack_doc(document: MealPlanDocument):
        meal_plan = json.loads(document.to_json())
        del meal_plan["_id"]["$oid"]
        print(meal_plan)
        meal_plan["uid"] = meal_plan["uid"]["$uuid"]

        meal_plan["startDate"] = meal_plan["startDate"]["$date"]
        meal_plan["endDate"] = meal_plan["endDate"]["$date"]

        meals = []
        for meal in meal_plan["meals"]:
            meal["date"] = meal["date"]["$date"]
            meals.append(Meal(**meal))

        meal_plan["meals"] = meals
        return MealPlan(**meal_plan)

    @staticmethod
    def today() -> str:
        """ Returns the meal slug for Today """
        meal_plan = MealPlanDocument.objects.order_by("startDate").limit(1)
        meal_plan = MealPlan._unpack_doc(meal_plan[0])

        for meal in meal_plan.meals:
            if meal.date == date.today():
                return meal.slug

        return "No Meal Today"

    @staticmethod
    def this_week():
        meal_plan = MealPlanDocument.objects.order_by("startDate").limit(1)
        meal_plan = MealPlan._unpack_doc(meal_plan[0])

        return meal_plan
