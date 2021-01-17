from typing import List

from app_config import USE_SQL

from db.db_base import BaseDocument
from db.db_setup import USE_SQL
from db.sql.db_session import create_session
from db.sql.meal_models import MealPlanModel


class _Meals(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "uid"
        self.sql_model = MealPlanModel
        self.create_session = create_session
