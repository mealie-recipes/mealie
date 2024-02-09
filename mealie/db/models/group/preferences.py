from typing import TYPE_CHECKING, Optional

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

    group_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped[Optional["Group"]] = orm.relationship("Group", back_populates="preferences")

    private_group: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    first_day_of_week: Mapped[int | None] = mapped_column(sa.Integer, default=0)

    # Recipe Defaults
    recipe_public: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    recipe_show_nutrition: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_show_assets: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_landscape_view: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_disable_comments: Mapped[bool | None] = mapped_column(sa.Boolean, default=False)
    recipe_disable_amount: Mapped[bool | None] = mapped_column(sa.Boolean, default=True)
    recipe_creation_tag: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("tags.id"), nullable=True, index=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
