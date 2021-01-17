from app_config import USE_SQL

from db.db_base import BaseDocument
from db.sql.db_session import create_session
from db.sql.recipe_models import RecipeModel


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        self.sql_model = RecipeModel
        self.create_session = create_session

    def save_new_sql(self, recipe_data: dict):
        session = self.create_session()
        new_recipe = self.sql_model(**recipe_data)
        session.add(new_recipe)
        session.commit()

        return recipe_data

    def update_image(self, slug: str, extension: str) -> None:
            pass
