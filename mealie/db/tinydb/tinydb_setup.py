from db.tinydb.baseclass import StoreBase
from settings import TINYDB_DIR

from tinydb import TinyDB


class TinyDatabase:
    def __init__(self) -> None:
        self.recipes = self._Recipes()
        self.meals = self._Meals()
        self.settings = self._Settings()
        self.themes = self._Themes()

    class _Recipes(StoreBase):
        def __init__(self) -> None:
            self.primary_key = "slug"
            self.store = TinyDB(TINYDB_DIR.joinpath("recipes.json"))

    class _Meals(StoreBase):
        def __init__(self) -> None:
            self.primary_key = "uid"
            self.store = TinyDB(TINYDB_DIR.joinpath("meals.json"))

    class _Settings(StoreBase):
        def __init__(self) -> None:
            self.primary_key = "name"
            self.store = TinyDB(TINYDB_DIR.joinpath("settings.json"))

    class _Themes(StoreBase):
        def __init__(self) -> None:
            self.primary_key = "name"
            self._store = TinyDB(TINYDB_DIR.joinpath("themes.json"))
