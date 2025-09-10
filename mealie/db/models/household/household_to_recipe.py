from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, UniqueConstraint, event
from sqlalchemy.engine.base import Connection
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.session import Session

from mealie.db.models._model_utils.datetime import NaiveDateTime

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..recipe import RecipeModel
    from .household import Household


class HouseholdToRecipe(SqlAlchemyBase, BaseMixins):
    __tablename__ = "households_to_recipes"
    __table_args__ = (UniqueConstraint("household_id", "recipe_id", name="household_id_recipe_id_key"),)
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    household: Mapped["Household"] = relationship("Household", viewonly=True)
    household_id = Column(GUID, ForeignKey("households.id"), index=True, primary_key=True)
    recipe: Mapped["RecipeModel"] = relationship("RecipeModel", viewonly=True)
    recipe_id = Column(GUID, ForeignKey("recipes.id"), index=True, primary_key=True)
    group_id: AssociationProxy[GUID] = association_proxy("household", "group_id")

    last_made: Mapped[datetime | None] = mapped_column(NaiveDateTime)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


def update_recipe_last_made(session: Session, target: HouseholdToRecipe):
    if not target.last_made:
        return

    from mealie.db.models.recipe.recipe import RecipeModel

    recipe = session.query(RecipeModel).filter(RecipeModel.id == target.recipe_id).first()
    if not recipe:
        return

    recipe.last_made = recipe.last_made or target.last_made
    recipe.last_made = max(recipe.last_made, target.last_made)


@event.listens_for(HouseholdToRecipe, "after_insert")
@event.listens_for(HouseholdToRecipe, "after_update")
@event.listens_for(HouseholdToRecipe, "after_delete")
def update_recipe_rating_on_insert_or_delete(_, connection: Connection, target: HouseholdToRecipe):
    session = Session(bind=connection)

    update_recipe_last_made(session, target)
    session.commit()
