from sqlalchemy import Column, ForeignKey, Integer, String, orm

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils import auto_init
from mealie.db.models._model_utils.guid import GUID


class RecipeComment(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_comments"
    id = Column(GUID, primary_key=True, default=GUID.generate)
    text = Column(String)

    # Recipe Link
    recipe_id = Column(Integer, ForeignKey("recipes.id"), nullable=False)
    recipe = orm.relationship("RecipeModel", back_populates="comments")

    # User Link
    user_id = Column(GUID, ForeignKey("users.id"), nullable=False)
    user = orm.relationship("User", back_populates="comments", single_parent=True, foreign_keys=[user_id])

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    def update(self, text, **_) -> None:
        self.text = text
