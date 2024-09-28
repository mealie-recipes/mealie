from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .household import Household


class HouseholdPreferencesModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "household_preferences"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    household_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("households.id"), nullable=False, index=True)
    household: Mapped[Optional["Household"]] = orm.relationship("Household", back_populates="preferences")
    group_id: AssociationProxy[GUID] = association_proxy("household", "group_id")

    private_household: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    lock_recipe_edits_from_other_households: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    first_day_of_week: Mapped[int | None] = mapped_column(sa.Integer, default=0)

    # Recipe Defaults
    recipe_public: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    recipe_show_nutrition: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_show_assets: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_landscape_view: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_disable_comments: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_disable_amount: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
