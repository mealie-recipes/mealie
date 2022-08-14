import sqlalchemy as sa
import sqlalchemy.orm as orm
from slugify import slugify
from sqlalchemy.orm import validates

from mealie.core import root_logger
from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils import guid

logger = root_logger.get_logger()

recipes_to_tags = sa.Table(
    "recipes_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", guid.GUID, sa.ForeignKey("recipes.id")),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id")),
)

plan_rules_to_tags = sa.Table(
    "plan_rules_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("plan_rule_id", guid.GUID, sa.ForeignKey("group_meal_plan_rules.id")),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id")),
)

cookbooks_to_tags = sa.Table(
    "cookbooks_to_tags",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", guid.GUID, sa.ForeignKey("cookbooks.id")),
    sa.Column("tag_id", guid.GUID, sa.ForeignKey("tags.id")),
)


class Tag(SqlAlchemyBase, BaseMixins):
    __tablename__ = "tags"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="tags_slug_group_id_key"),)
    id = sa.Column(guid.GUID, primary_key=True, default=guid.GUID.generate)

    # ID Relationships
    group_id = sa.Column(guid.GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="tags", foreign_keys=[group_id])

    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, nullable=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes_to_tags, back_populates="tags")

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(self, name, group_id, **_) -> None:
        self.group_id = group_id
        self.name = name.strip()
        self.slug = slugify(self.name)

    @classmethod  # TODO: Remove this
    def get_ref(cls, match_value: str, session=None):  # type: ignore
        if not session or not match_value:
            return None

        slug = slugify(match_value)

        if result := session.query(Tag).filter(Tag.slug == slug).one_or_none():
            logger.debug("Category exists, associating recipe")
            return result
        else:
            logger.debug("Category doesn't exists, creating Category")
            return Tag(name=match_value)  # type: ignore
