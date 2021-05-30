from datetime import datetime

from mealie.db.models.model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.users import User
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, orm


class RecipeComment(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_comments"
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey("recipes.id"))
    recipe = orm.relationship("RecipeModel", back_populates="comments")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = orm.relationship("User", back_populates="comments", single_parent=True, foreign_keys=[user_id])
    date_added = Column(DateTime, default=datetime.now)
    text = Column(String)

    def __init__(self, recipe_slug, user, text, session, **_) -> None:
        self.text = text
        self.user = User.get_ref(session, user)
        self.recipe = RecipeModel.get_ref(session, recipe_slug, "slug")

    def update(self, text, **_) -> None:
        self.text = text
