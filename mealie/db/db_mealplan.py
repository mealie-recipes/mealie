from typing import List

from settings import USE_MONGO, USE_SQL

from db.db_base import BaseDocument
from db.db_setup import USE_MONGO, USE_SQL, tiny_db
from db.mongo.meal_models import MealDocument, MealPlanDocument


class _Meals(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "uid"
        if USE_SQL:
            self.sql_model = None
        self.document = MealPlanDocument

    @staticmethod
    def _process_meals(meals: List[dict]) -> List[MealDocument]:
        """Turns a list of Meals in dictionary form into a list of
        MealDocuments that can be attached to a MealPlanDocument


        Args: \n
            meals (List[dict]): From a Pydantic Class in meal_services.py \n

        Returns:
            a List of MealDocuments
        """
        meal_docs = []
        for meal in meals:
            meal_doc = MealDocument(**meal)
            meal_docs.append(meal_doc)

        return meal_docs

    def save_new(self, plan_data: dict) -> None:
        """Saves a new meal plan into the database

        Args: \n
            plan_data (dict): From a Pydantic Class in meal_services.py \n
        """

        if USE_MONGO:
            plan_data["meals"] = _Meals._process_meals(plan_data["meals"])
            document = self.document(**plan_data)

            document.save()
        elif USE_SQL:
            pass

    def update(self, uid: str, plan_data: dict) -> dict:
        if USE_MONGO:
            document = self.document.objects.get(uid=uid)
            if document:
                new_meals = _Meals._process_meals(plan_data["meals"])
                document.update(set__meals=new_meals)
                document.save()
        elif USE_SQL:
            pass
