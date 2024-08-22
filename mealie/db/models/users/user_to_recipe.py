from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, Float, ForeignKey, UniqueConstraint, event
from sqlalchemy.engine.base import Connection
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.session import Session

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..recipe import RecipeModel


class UserToRecipe(SqlAlchemyBase, BaseMixins):
    __tablename__ = "users_to_recipes"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="user_id_recipe_id_rating_key"),)
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    user_id = Column(GUID, ForeignKey("users.id"), index=True, primary_key=True)
    recipe: Mapped["RecipeModel"] = relationship("RecipeModel")
    recipe_id = Column(GUID, ForeignKey("recipes.id"), index=True, primary_key=True)
    group_id: AssociationProxy[GUID] = association_proxy("recipe", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("recipe", "household_id")

    rating = Column(Float, index=True, nullable=True)
    is_favorite = Column(Boolean, index=True, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


def update_recipe_rating(session: Session, target: UserToRecipe):
    from mealie.db.models.recipe.recipe import RecipeModel

    recipe = session.query(RecipeModel).filter(RecipeModel.id == target.recipe_id).first()
    if not recipe:
        return

    recipe.rating = -1  # this will trigger the recipe to re-calculate the rating


@event.listens_for(UserToRecipe, "after_insert")
@event.listens_for(UserToRecipe, "after_update")
@event.listens_for(UserToRecipe, "after_delete")
def update_recipe_rating_on_insert_or_delete(_, connection: Connection, target: UserToRecipe):
    session = Session(bind=connection)

    update_recipe_rating(session, target)
    session.commit()
