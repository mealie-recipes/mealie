from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mealie.db.models._model_utils.datetime import NaiveDateTime

from .._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..users import User
    from . import RecipeModel


class RecipeTimelineEvent(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_timeline_events"
    id: FilterableColumn[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # Parent Recipe
    recipe_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("recipes.id"), nullable=False, index=True)
    recipe: Mapped["RecipeModel"] = relationship("RecipeModel", back_populates="timeline_events")

    group_id: AssociationProxy[GUID] = association_proxy("recipe", "group_id")
    household_id: AssociationProxy[GUID] = association_proxy("recipe", "household_id")

    # Related User (Actor)
    user_id: FilterableColumn[GUID] = mapped_column(GUID, ForeignKey("users.id"), nullable=False, index=True)
    user: Mapped["User"] = relationship(
        "User", back_populates="recipe_timeline_events", single_parent=True, foreign_keys=[user_id]
    )

    # General Properties
    subject: FilterableColumn[str] = mapped_column(String, nullable=False)
    message: FilterableColumn[str | None] = mapped_column(String)
    event_type: FilterableColumn[str | None] = mapped_column(String)
    image: FilterableColumn[str | None] = mapped_column(String)

    # Timestamps
    timestamp: FilterableColumn[datetime | None] = mapped_column(NaiveDateTime, index=True)

    @auto_init()
    def __init__(
        self,
        timestamp=None,
        **_,
    ) -> None:
        self.timestamp = timestamp or datetime.now(UTC)
