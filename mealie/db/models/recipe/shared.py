from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mealie.db.models._model_base import BaseMixins, FilterableColumn, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.datetime import NaiveDateTime
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from . import RecipeModel


def defaut_expires_at_time() -> datetime:
    return datetime.now(UTC) + timedelta(days=30)


class RecipeShareTokenModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_share_tokens"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=uuid4)

    group_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)

    recipe_id: FilterableColumn[GUID] = mapped_column(GUID, sa.ForeignKey("recipes.id"), nullable=False, index=True)
    recipe: Mapped["RecipeModel"] = relationship("RecipeModel", back_populates="share_tokens", uselist=False)

    expires_at: FilterableColumn[datetime] = mapped_column(NaiveDateTime, nullable=False)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
