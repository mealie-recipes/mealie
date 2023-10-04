from sqlalchemy import Column, ForeignKey, Table, UniqueConstraint

from .._model_base import SqlAlchemyBase
from .._model_utils import GUID

users_to_favorites = Table(
    "users_to_favorites",
    SqlAlchemyBase.metadata,
    Column("user_id", GUID, ForeignKey("users.id"), index=True),
    Column("recipe_id", GUID, ForeignKey("recipes.id"), index=True),
    UniqueConstraint("user_id", "recipe_id", name="user_id_recipe_id_key"),
)
