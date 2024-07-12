from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from .household import Household


class GroupRecipeAction(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_actions"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), index=True)
    group: Mapped["Group"] = relationship("Group", back_populates="recipe_actions", single_parent=True)
    household_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("households.id"), index=True)
    household: Mapped["Household"] = relationship("Household", back_populates="recipe_actions")

    action_type: Mapped[str] = mapped_column(String, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    url: Mapped[str] = mapped_column(String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
