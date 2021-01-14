from datetime import date, datetime

from db.tinydb.baseclass import StoreBase
from settings import TINYDB_DIR
from tinydb_serialization import SerializationMiddleware, Serializer

from tinydb import TinyDB


class DateSerializer(Serializer):
    OBJ_CLASS = date  # The class handles date objects

    def encode(self, obj):
        """
        Serialize the naive date object without conversion.
        """
        return obj.strftime("%Y%m%d")

    def decode(self, s):
        """
        Return the serialization as a date object.
        """
        return datetime.strptime(s, "%Y%m%d").date()


class DateTimeSerializer(Serializer):
    OBJ_CLASS = datetime  # The class this serializer handles

    def encode(self, obj):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")

    def decode(self, s):
        return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S")


serialization = SerializationMiddleware()
serialization.register_serializer(DateTimeSerializer(), "TinyDateTime")
serialization.register_serializer(DateSerializer(), "TinyDate")


class TinyDatabase:
    def __init__(self) -> None:
        self.db = TinyDB(TINYDB_DIR.joinpath("db.json"), storage=serialization)

        self.recipes = self._Recipes(self.db)
        self.meals = self._Meals(self.db)
        self.settings = self._Settings(self.db)
        self.themes = self._Themes(self.db)

    class _Recipes(StoreBase):
        def __init__(self, db) -> None:
            self.primary_key = "slug"
            self.store = db.table("recipes")

    class _Meals(StoreBase):
        def __init__(self, db) -> None:
            self.primary_key = "uid"
            self.store = db.table("meals")

    class _Settings(StoreBase):
        def __init__(self, db) -> None:
            self.primary_key = "name"
            self.store = db.table("settings")

    class _Themes(StoreBase):
        def __init__(self, db) -> None:
            self.primary_key = "name"
            self.store = db.table("themes")
