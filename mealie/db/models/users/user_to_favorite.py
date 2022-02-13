from sqlalchemy import Column, ForeignKey, Table

from .._model_base import SqlAlchemyBase
from .._model_utils import GUID

users_to_favorites = Table(
    "users_to_favorites",
    SqlAlchemyBase.metadata,
    Column("user_id", GUID, ForeignKey("users.id")),
    Column("recipe_id", GUID, ForeignKey("recipes.id")),
)
