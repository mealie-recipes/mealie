import mongoengine
from settings import USE_MONGO, USE_TINYDB

from db.mongo.meal_models import MealDocument, MealPlanDocument
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

    def get(self, match_value: str, match_key: str = None, limit=1) -> dict:
        if USE_MONGO:
            return self._document.objects.get(match_key=match_value).limit(limit)
        elif USE_TINYDB:
            return self.store.get(match_value, match_key)

    def save_new(self, document: dict) -> str:
        if USE_MONGO:
            self._document = self._document(**document)
            self._document.save()
            return self._document.slug
        elif USE_TINYDB:
            return self.store.save(document)

    def update(self) -> dict:
        if USE_MONGO:
            pass
        elif USE_TINYDB:
            pass

    def delete(self) -> dict:
        if USE_MONGO:
            pass
        elif USE_TINYDB:
            pass


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
            pass

    class _Meals(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "uid"
            if USE_TINYDB:
                self.store = tiny_db.meals
            self.document = MealPlanDocument
            pass

    class _Settings(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "name"
            if USE_TINYDB:
                self.store = tiny_db.settings
            self.document = SiteSettingsDocument
            pass

    class _Themes(BaseDocument):
        def __init__(self) -> None:
            self.primary_key = "name"
            if USE_TINYDB:
                self.store = tiny_db.themes
            self.document = SiteThemeDocument
            pass


db = Database()
