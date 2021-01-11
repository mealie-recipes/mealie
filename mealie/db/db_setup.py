import json

import mongoengine
from settings import USE_MONGO, USE_TINYDB

from db.mongo.meal_models import MealPlanDocument
from db.mongo.recipe_models import RecipeDocument
from db.mongo.settings_models import SiteSettingsDocument, SiteThemeDocument
from db.tinydb.baseclass import StoreBase

"""
Common Actions:
    - [ ] Create
    - [ ] Read
    - [ ] Update
    - [ ] Delete
    - [ ] Unpack Document Mongo Mostly.
    - [ ] Query by Primary Key

Recipe Actions
    - [ ] Query by Category
    - [ ] Query by dateAdded

Progress:
    - [x] Recipes
    - [ ] MealPlans
    - [ ] Site Settings
    - [ ] Themes

"""

if USE_TINYDB:
    from db.tinydb.tinydb_setup import TinyDatabase

    tiny_db = TinyDatabase()

elif USE_MONGO:
    from db.mongo.mongo_setup import global_init as mongo_global_init

    mongo_global_init()


class BaseDocument:
    def __init__(self) -> None:
        self.primary_key: str
        self.store: StoreBase
        self._document: mongoengine.Document

    @staticmethod
    def _unpack_mongo(document) -> dict:
        document = json.loads(document.to_json())
        del document["_id"]

        document["dateAdded"] = document["dateAdded"]["$date"]

        return document

    def get_all(self, limit: int = None, order_by: str = "dateAdded") -> list[dict]:
        if USE_MONGO:
            documents = self._document.objects.order_by(str(order_by)).limit(limit)
            docs = []
            for item in documents:
                doc = BaseDocument._unpack_mongo(item)
                docs.append(doc)

            return docs

        elif USE_TINYDB:
            return self.store.get_all()

    def get(self, match_value: str, match_key: str = None, limit=1) -> dict:
        if USE_MONGO:
            document = self._document.objects.get(**{str(match_key): match_value})
            return BaseDocument._unpack_mongo(document)

        elif USE_TINYDB:
            return self.store.get(match_value, match_key, limit=limit)

    def save_new(self, document: dict) -> str:
        if USE_MONGO:
            new_document = self._document(**document)
            new_document.save()
            return new_document.slug
        elif USE_TINYDB:
            return self.store.save(document)

    def delete(self, primary_key) -> dict:
        if USE_MONGO:
            document = self._document.objects.get(
                **{str(self.primary_key): primary_key}
            )

            if document:
                document.delete()
            return "Document Deleted"
        elif USE_TINYDB:
            self.store.delete(primary_key)


class Database:
    def __init__(self) -> None:
        self.recipes = self._Recipes()
        self.meals = self._Meals()
        self.settings = self._Settings()
        self.themes = self._Themes()

    class _Recipes(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "slug"
            if USE_TINYDB:
                self.store = tiny_db.recipes
            self._document = RecipeDocument

        def update(self, slug: str, new_data: dict) -> None:
            if USE_MONGO:
                document = self._document.objects.get(slug=slug)

                if document:
                    document.update(set__name=new_data.get("name"))
                    document.update(set__description=new_data.get("description"))
                    document.update(set__image=new_data.get("image"))
                    document.update(set__recipeYield=new_data.get("recipeYield"))
                    document.update(
                        set__recipeIngredient=new_data.get("recipeIngredient")
                    )
                    document.update(
                        set__recipeInstructions=new_data.get("recipeInstructions")
                    )
                    document.update(set__totalTime=new_data.get("totalTime"))

                    document.update(set__categories=new_data.get("categories"))
                    document.update(set__tags=new_data.get("tags"))
                    document.update(set__notes=new_data.get("notes"))
                    document.update(set__orgURL=new_data.get("orgURL"))
                    document.update(set__rating=new_data.get("rating"))
                    document.update(set__extras=new_data.get("extras"))
                    document.save()
            elif USE_TINYDB:
                self.store.update_doc(slug, new_data)

        def update_image(self, slug: str, extension: str) -> None:
            if USE_MONGO:
                document = self._document.objects.get(slug=slug)

                if document:
                    document.update(set__image=f"{slug}.{extension}")
            elif USE_TINYDB:
                self.store.update_doc(slug, {"image": f"{slug}.{extension}"})

    class _Meals(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "uid"
            if USE_TINYDB:
                self.store = tiny_db.meals
            self.document = MealPlanDocument

            def update(self, key: str, new_data: dict) -> dict:
                if USE_MONGO:
                    pass
                elif USE_TINYDB:
                    pass

    class _Settings(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "name"
            if USE_TINYDB:
                self.store = tiny_db.settings
            self.document = SiteSettingsDocument

            def update(self, key: str, new_data: dict) -> dict:
                if USE_MONGO:
                    pass
                elif USE_TINYDB:
                    pass

    class _Themes(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "name"
            if USE_TINYDB:
                self.store = tiny_db.themes
            self.document = SiteThemeDocument

            def update(self, key: str, new_data: dict) -> dict:
                if USE_MONGO:
                    pass
                elif USE_TINYDB:
                    pass


db = Database()
