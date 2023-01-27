from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from group import Group


class GroupPreferencesModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "group_preferences"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="preferences")

    private_group: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    first_day_of_week: Mapped[int] = mapped_column(sa.Integer, default=0)

    # Recipe Defaults
    recipe_public: Mapped[bool] = mapped_column(sa.Boolean, default=True)
    recipe_show_nutrition: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    recipe_show_assets: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    recipe_landscape_view: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    recipe_disable_comments: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    recipe_disable_amount: Mapped[bool] = mapped_column(sa.Boolean, default=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
