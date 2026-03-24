from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.datetime import NaiveDateTime, get_utc_now
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from ..users import User
    from .recipe import RecipeModel


class RecipeVersion(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_versions"
    __table_args__ = (sa.Index("ix_recipe_versions_recipe_id_version", "recipe_id", "version_number"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    recipe_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    recipe: Mapped[Optional["RecipeModel"]] = orm.relationship("RecipeModel", back_populates="versions")

    user_id: Mapped[GUID | None] = mapped_column(GUID, sa.ForeignKey("users.id"), nullable=True)
    user: Mapped[Optional["User"]] = orm.relationship("User", uselist=False)

    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped[Optional["Group"]] = orm.relationship("Group", uselist=False)

    version_number: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    name: Mapped[str] = mapped_column(sa.String, nullable=False)
    snapshot: Mapped[str] = mapped_column(sa.Text, nullable=False)

    created_at: Mapped[NaiveDateTime | None] = mapped_column(NaiveDateTime, default=get_utc_now)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
