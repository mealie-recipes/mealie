import sqlalchemy as sa
import sqlalchemy.orm as orm
from mealie.core import root_logger
from mealie.db.models.model_base import SqlAlchemyBase
from slugify import slugify
from sqlalchemy.orm import validates

logger = root_logger.get_logger()

recipes2tags = sa.Table(
    "recipes2tags",
    SqlAlchemyBase.metadata,
    sa.Column("recipe_id", sa.Integer, sa.ForeignKey("recipes.id")),
    sa.Column("tag_id", sa.Integer, sa.ForeignKey("tags.id")),
)


class Tag(SqlAlchemyBase):
    __tablename__ = "tags"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True, nullable=False)
    slug = sa.Column(sa.String, index=True, unique=True, nullable=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes2tags, back_populates="tags")

    @validates("name")
    def validate_name(self, key, name):
        assert name != ""
        return name

    def __init__(self, name, session=None) -> None:
        self.name = name.strip()
        self.slug = slugify(self.name)

    def update(self, name, session=None) -> None:
        self.__init__(name, session)

    @staticmethod
    def create_if_not_exist(session, name: str = None):
        test_slug = slugify(name)
        result = session.query(Tag).filter(Tag.slug == test_slug).one_or_none()

        if result:
            logger.debug("Tag exists, associating recipe")
            return result
        else:
            logger.debug("Tag doesn't exists, creating tag")
            return Tag(name=name)
