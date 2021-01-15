from settings import USE_MONGO, USE_SQL

from db.db_base import BaseDocument
from db.mongo.recipe_models import RecipeDocument
from db.sql.db_session import create_session
from db.sql.recipe_models import RecipeModel


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        if USE_SQL:
            self.sql_model = RecipeModel
            self.create_session = create_session
        else:
            self.document = RecipeDocument

    def save_new_sql(self, recipe_data: dict):
        session = self.create_session()
        new_recipe = self.sql_model(**recipe_data)
        session.add(new_recipe)
        session.commit()

        return recipe_data

    def update(self, slug: str, new_data: dict) -> None:
        if USE_MONGO:
            document = self.document.objects.get(slug=slug)

            if document:
                document.update(set__name=new_data.get("name"))
                document.update(set__description=new_data.get("description"))
                document.update(set__image=new_data.get("image"))
                document.update(set__recipeYield=new_data.get("recipeYield"))
                document.update(set__recipeIngredient=new_data.get("recipeIngredient"))
                document.update(
                    set__recipeInstructions=new_data.get("recipeInstructions")
                )
                document.update(set__totalTime=new_data.get("totalTime"))

                document.update(set__slug=new_data.get("slug"))
                document.update(set__categories=new_data.get("categories"))
                document.update(set__tags=new_data.get("tags"))
                document.update(set__notes=new_data.get("notes"))
                document.update(set__orgURL=new_data.get("orgURL"))
                document.update(set__rating=new_data.get("rating"))
                document.update(set__extras=new_data.get("extras"))
                document.save()

                return new_data.get("slug")
        elif USE_SQL:
            session, recipe = self._query_one(match_value=slug)
            recipe.update(**new_data)
            recipe_dict = recipe.dict()
            session.commit()

            session.close()

            return recipe_dict

    def update_image(self, slug: str, extension: str) -> None:
        if USE_MONGO:
            document = self.document.objects.get(slug=slug)

            if document:
                document.update(set__image=f"{slug}.{extension}")
        elif USE_SQL:
            pass
