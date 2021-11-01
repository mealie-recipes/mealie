import sqlalchemy as sa
import sqlalchemy.orm as orm
from slugify import slugify
from sqlalchemy.orm import validates

from mealie.core import root_logger
from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase

logger = root_logger.get_logger()


group2categories = sa.Table(
    "group2categories",
    SqlAlchemyBase.metadata,
    sa.Column("group_id", sa.Integer, sa.ForeignKey("groups.id")),
    sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id")),
)

recipes2categories = sa.Table(
    "recipes2categories",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id")),
    sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id")),
)

cookbooks_to_categories = sa.Table(
    "cookbooks_to_categories",
    SqlAlchemyBase.metadata,
    sa.Column("cookbook_id", sa.Integer, sa.ForeignKey("cookbooks.id")),
    sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id")),
)


class Category(SqlAlchemyBase, BaseMixins):
    __tablename__ = "categories"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, unique=True, nullable=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes2categories, back_populates="recipe_category")

    class Config:
        get_attr = "slug"

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(self, name, **_) -> None:
        self.name = name.strip()
        self.slug = slugify(name)

    @classmethod
    def get_ref(cls, match_value: str, session=None):
        if not session or not match_value:
            return None

        slug = slugify(match_value)

        result = session.query(Category).filter(Category.slug == slug).one_or_none()
        if result:
            logger.debug("Category exists, associating recipe")
            return result
        else:
            logger.debug("Category doesn't exists, creating Category")
            return Category(name=match_value)
