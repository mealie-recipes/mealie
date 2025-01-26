from typing import TYPE_CHECKING

from pydantic import ConfigDict
from slugify import slugify
from sqlalchemy import Boolean, Column, ForeignKey, String, Table, UniqueConstraint, orm
from sqlalchemy.orm import Mapped, mapped_column

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils.auto_init import auto_init
from mealie.db.models._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group
    from ..household import Household
    from . import RecipeModel

households_to_tools = Table(
    "households_to_tools",
    SqlAlchemyBase.metadata,
    Column("household_id", GUID, ForeignKey("households.id"), index=True),
    Column("tool_id", GUID, ForeignKey("tools.id"), index=True),
    UniqueConstraint("household_id", "tool_id", name="household_id_tool_id_key"),
)

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

    households_with_tool: Mapped[list["Household"]] = orm.relationship(
        "Household", secondary=households_to_tools, back_populates="tools_on_hand"
    )
    recipes: Mapped[list["RecipeModel"]] = orm.relationship(
        "RecipeModel", secondary=recipes_to_tools, back_populates="tools"
    )

    model_config = ConfigDict(
        exclude={
            "households_with_tool",
        }
    )

    # Deprecated
    on_hand: Mapped[bool | None] = mapped_column(Boolean, default=False)

    @auto_init()
    def __init__(
        self, session: orm.Session, group_id: GUID, name: str, households_with_tool: list[str] | None = None, **_
    ) -> None:
        from ..household import Household

        self.slug = slugify(name)

        if not households_with_tool:
            self.households_with_tool = []
        else:
            self.households_with_tool = (
                session.query(Household)
                .filter(Household.group_id == group_id, Household.slug.in_(households_with_tool))
                .all()
            )
