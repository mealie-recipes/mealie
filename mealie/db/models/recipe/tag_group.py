from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from slugify import slugify
from sqlalchemy.orm import Mapped, mapped_column, validates

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from .tag import Tag


class TagGroup(SqlAlchemyBase, BaseMixins):
    __tablename__ = "tag_groups"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="tag_groups_slug_group_id_key"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    group_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(sa.String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(sa.String, index=True, nullable=False)
    color: Mapped[str | None] = mapped_column(sa.String, nullable=True)
    position: Mapped[int] = mapped_column(sa.Integer, default=0, nullable=False)

    group: Mapped["Group"] = orm.relationship("Group", back_populates="tag_groups", foreign_keys=[group_id])
    tags: Mapped[list["Tag"]] = orm.relationship("Tag", back_populates="tag_group")

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(self, name, group_id, **kwargs) -> None:
        self.group_id = group_id
        self.name = name.strip()
        self.slug = slugify(self.name)
        self.color = kwargs.get("color")
        self.position = kwargs.get("position", 0)
