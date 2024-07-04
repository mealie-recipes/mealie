from typing import TYPE_CHECKING

from slugify import slugify
from sqlalchemy import Boolean, Column, ForeignKey, String, Table, UniqueConstraint, orm
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from . import RecipeModel

recipes_to_tools = Table(
    "recipes_to_tools",
    SqlAlchemyBase.metadata,
    Column("recipe_id", GUID, ForeignKey("recipes.id"), index=True),
    Column("tool_id", GUID, ForeignKey("tools.id"), index=True),
    UniqueConstraint("recipe_id", "tool_id", name="recipe_id_tool_id_key"),
)

cookbooks_to_tools = Table(
    "cookbooks_to_tools",
    SqlAlchemyBase.metadata,
    Column("cookbook_id", GUID, ForeignKey("cookbooks.id"), index=True),
    Column("tool_id", GUID, ForeignKey("tools.id"), index=True),
    UniqueConstraint("cookbook_id", "tool_id", name="cookbook_id_tool_id_key"),
)


class Tool(SqlAlchemyBase, BaseMixins):
    __tablename__ = "tools"
    __table_args__ = (UniqueConstraint("slug", "group_id", name="tools_slug_group_id_key"),)
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="tools", foreign_keys=[group_id])

    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String, index=True, nullable=False)
    on_hand: Mapped[bool | None] = mapped_column(Boolean, default=False)
    recipes: Mapped[list["RecipeModel"]] = orm.relationship(
        "RecipeModel", secondary=recipes_to_tools, back_populates="tools"
    )

    @auto_init()
    def __init__(self, name, **_) -> None:
        self.slug = slugify(name)
