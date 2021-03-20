import sqlalchemy as sa
import sqlalchemy.orm as orm
from mealie.db.models.model_base import SqlAlchemyBase
from fastapi.logger import logger
from slugify import slugify
from sqlalchemy.orm import validates

recipes2tags = sa.Table(
    "recipes2tags",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id")),
    sa.Column("tag_slug", sa.Integer, sa.ForeignKey("tags.slug")),
)


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, unique=True, nullable=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes2tags, back_populates="tags")

    @validates("name")
    def validate_name(self, key, name):
        assert not name == ""
        return name

    def __init__(self, name) -> None:
        self.name = name.strip()
        self.slug = slugify(self.name)

    @staticmethod
    def create_if_not_exist(session, name: str = None):
        test_slug = slugify(name)
        try:
            result = session.query(Tag).filter(Tag.slug == test_slug).first()

            if result:
                logger.info("Tag exists, associating recipe")

                return result
            else:
                logger.info("Tag doesn't exists, creating tag")
                return Tag(name=name)
        except:
            logger.info("Tag doesn't exists, creating tag")
            return Tag(name=name)
