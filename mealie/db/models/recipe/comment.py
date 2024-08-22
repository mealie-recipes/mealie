from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User
    from . import RecipeModel


class RecipeComment(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_comments"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    text: Mapped[str | None] = mapped_column(String)

    # Recipe Link
    recipe_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("recipes.id"), nullable=False, index=True)
    recipe: Mapped["RecipeModel"] = orm.relationship("RecipeModel", back_populates="comments")

    group_id: AssociationProxy[GUID] = association_proxy("recipe", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("recipe", "household_id")

    # User Link
    user_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = orm.relationship(
        "User", back_populates="comments", single_parent=True, foreign_keys=[user_id]
    )

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    def update(self, text, **_) -> None:
        self.text = text
