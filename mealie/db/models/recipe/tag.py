from typing import TYPE_CHECKING

import sqlalchemy as sa
import sqlalchemy.orm as orm
from slugify import slugify
from sqlalchemy.orm import Mapped, mapped_column, validates

from mealie.core import root_logger
from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils import guid

if TYPE_CHECKING:
    from ..group import Group
    from . import RecipeModel


logger = root_logger.get_logger()

recipes_to_tags = sa.Table(
    "recipes_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", guid.GUID, sa.ForeignKey("recipes.id"), index=True),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id"), index=True),
    sa.UniqueConstraint("recipe_id", "tag_id", name="recipe_id_tag_id_key"),
)

plan_rules_to_tags = sa.Table(
    "plan_rules_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("plan_rule_id", guid.GUID, sa.ForeignKey("group_meal_plan_rules.id"), index=True),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id"), index=True),
    sa.UniqueConstraint("plan_rule_id", "tag_id", name="plan_rule_id_tag_id_key"),
)

cookbooks_to_tags = sa.Table(
    "cookbooks_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", guid.GUID, sa.ForeignKey("cookbooks.id"), index=True),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id"), index=True),
    sa.UniqueConstraint("cookbook_id", "tag_id", name="cookbook_id_tag_id_key"),
)


class Tag(SqlAlchemyBase, BaseMixins):
    __tablename__ = "tags"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="tags_slug_group_id_key"),)
    id: Mapped[guid.GUID] = mapped_column(guid.GUID, primary_key=True, default=guid.GUID.generate)

    # ID Relationships
    group_id: Mapped[guid.GUID] = mapped_column(guid.GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="tags", foreign_keys=[group_id])

    name: Mapped[str] = mapped_column(sa.String, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(sa.String, index=True, nullable=False)
    recipes: Mapped[list["RecipeModel"]] = orm.relationship(
        "RecipeModel", secondary=recipes_to_tags, back_populates="tags"
    )

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(self, name, group_id, **_) -> None:
        self.group_id = group_id
        self.name = name.strip()
        self.slug = slugify(self.name)
