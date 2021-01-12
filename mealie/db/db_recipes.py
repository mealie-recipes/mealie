from settings import USE_MONGO, USE_TINYDB

from db.db_base import BaseDocument
from db.db_setup import tiny_db
from db.mongo.recipe_models import RecipeDocument


class _Recipes(BaseDocument):
    def __init__(self) -> None:
        self.primary_key = "slug"
        if USE_TINYDB:
            self.store = tiny_db.recipes
        self.document = RecipeDocument

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
        elif USE_TINYDB:
            self.store.update_doc(slug, new_data)
            return new_data.get("slug")

    def update_image(self, slug: str, extension: str) -> None:
        if USE_MONGO:
            document = self.document.objects.get(slug=slug)

            if document:
                document.update(set__image=f"{slug}.{extension}")
        elif USE_TINYDB:
            self.store.update_doc(slug, {"image": f"{slug}.{extension}"})
