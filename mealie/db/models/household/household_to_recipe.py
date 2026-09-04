from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, UniqueConstraint
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
