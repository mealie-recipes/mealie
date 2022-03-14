import sqlalchemy as sa
import sqlalchemy.orm as orm
from slugify import slugify
from sqlalchemy.orm import validates

from mealie.core import root_logger

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.guid import GUID

logger = root_logger.get_logger()


group_to_categories = sa.Table(
    "group_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("group_id", GUID, sa.ForeignKey("groups.id")),
    sa.Column("category_id", GUID, sa.ForeignKey("categories.id")),
)

plan_rules_to_categories = sa.Table(
    "plan_rules_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("group_plan_rule_id", GUID, sa.ForeignKey("group_meal_plan_rules.id")),
    sa.Column("category_id", GUID, sa.ForeignKey("categories.id")),
)

recipes_to_categories = sa.Table(
    "recipes_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", GUID, sa.ForeignKey("recipes.id")),
    sa.Column("category_id", GUID, sa.ForeignKey("categories.id")),
)

cookbooks_to_categories = sa.Table(
    "cookbooks_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", GUID, sa.ForeignKey("cookbooks.id")),
    sa.Column("category_id", GUID, sa.ForeignKey("categories.id")),
)


class Category(SqlAlchemyBase, BaseMixins):
    __tablename__ = "categories"
    __table_args__ = (sa.UniqueConstraint("slug", "group_id", name="category_slug_group_id_key"),)

    # ID Relationships
    group_id = sa.Column(GUID, sa.ForeignKey("groups.id"), nullable=False, index=True)
    group = orm.relationship("Group", back_populates="categories", foreign_keys=[group_id])

    id = sa.Column(GUID, primary_key=True, default=GUID.generate)
    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, nullable=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes_to_categories, back_populates="recipe_category")

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(self, name, group_id, **_) -> None:
        self.group_id = group_id
        self.name = name.strip()
        self.slug = slugify(name)

    @classmethod  # TODO: Remove this
    def get_ref(cls, match_value: str, session=None):  # type: ignore
        if not session or not match_value:
            return None

        slug = slugify(match_value)

        result = session.query(Category).filter(Category.slug == slug).one_or_none()
        if result:
            logger.debug("Category exists, associating recipe")
            return result
        else:
            logger.debug("Category doesn't exists, creating Category")
            return Category(name=match_value)  # type: ignore
