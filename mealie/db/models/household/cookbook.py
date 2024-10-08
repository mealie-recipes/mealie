from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, UniqueConstraint, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils import guid
from .._model_utils.auto_init import auto_init
from ..recipe.category import Category, cookbooks_to_categories
from ..recipe.tag import Tag, cookbooks_to_tags
from ..recipe.tool import Tool, cookbooks_to_tools

if TYPE_CHECKING:
    from ..group import Group
    from .household import Household


class CookBook(SqlAlchemyBase, BaseMixins):
    __tablename__ = "cookbooks"
    __table_args__: tuple[UniqueConstraint, ...] = (
        UniqueConstraint("slug", "group_id", name="cookbook_slug_group_id_key"),
    )

    id: Mapped[guid.GUID] = mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    group_id: Mapped[guid.GUID | None] = mapped_column(guid.GUID, ForeignKey("groups.id"), index=True)
    group: Mapped[Optional["Group"]] = orm.relationship("Group", back_populates="cookbooks")
    household_id: Mapped[guid.GUID | None] = mapped_column(guid.GUID, ForeignKey("households.id"), index=True)
    household: Mapped[Optional["Household"]] = orm.relationship("Household", back_populates="cookbooks")

    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String, default="")
    public: Mapped[str | None] = mapped_column(Boolean, default=False)
    query_filter_string: Mapped[str] = mapped_column(String, nullable=False, default="")

    # Old filters - deprecated in favor of query filter strings
    categories: Mapped[list[Category]] = orm.relationship(
        Category, secondary=cookbooks_to_categories, single_parent=True
    )
    require_all_categories: Mapped[bool | None] = mapped_column(Boolean, default=True)

    tags: Mapped[list[Tag]] = orm.relationship(Tag, secondary=cookbooks_to_tags, single_parent=True)
    require_all_tags: Mapped[bool | None] = mapped_column(Boolean, default=True)

    tools: Mapped[list[Tool]] = orm.relationship(Tool, secondary=cookbooks_to_tools, single_parent=True)
    require_all_tools: Mapped[bool | None] = mapped_column(Boolean, default=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass

    def update(self, *args, **kwarg):
        self.__init__(*args, **kwarg)
