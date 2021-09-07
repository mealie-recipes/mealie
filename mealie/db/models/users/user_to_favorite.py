from sqlalchemy import Column, ForeignKey, Integer, Table

from .._model_base import SqlAlchemyBase

users_to_favorites = Table(
    "users_to_favorites",
    SqlAlchemyBase.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
)
