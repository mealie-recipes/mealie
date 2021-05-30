from datetime import datetime
from uuid import uuid4

from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users import User
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, orm


def generate_uuid():
    return str(uuid4())


class RecipeComment(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_comments"
    id = Column(Integer, primary_key=True)
    uuid = Column(String, unique=True, nullable=False, default=generate_uuid)
    parent_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    recipe = orm.relationship("RecipeModel", back_populates="comments")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = orm.relationship("User", back_populates="comments", single_parent=True, foreign_keys=[user_id])
    date_added = Column(DateTime, default=datetime.now)
    text = Column(String)

    def __init__(self, recipe_slug, user, text, session, date_added=None, **_) -> None:
        self.text = text
        self.recipe = RecipeModel.get_ref(session, recipe_slug, "slug")
        self.date_added = date_added or datetime.now()

        if isinstance(user, dict):
            user = user.get("id")

        self.user = User.get_ref(session, user)

    def update(self, text, **_) -> None:
        self.text = text
