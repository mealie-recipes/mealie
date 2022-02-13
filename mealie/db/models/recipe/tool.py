from slugify import slugify
from sqlalchemy import Boolean, Column, ForeignKey, String, Table, UniqueConstraint, orm

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils import auto_init
from mealie.db.models._model_utils.guid import GUID

recipes_to_tools = Table(
    "recipes_to_tools",
    SqlAlchemyBase.metadata,
    Column("recipe_id", GUID, ForeignKey("recipes.id")),
    Column("tool_id", GUID, ForeignKey("tools.id")),
)


class Tool(SqlAlchemyBase, BaseMixins):
    __tablename__ = "tools"
    id = Column(GUID, primary_key=True, default=GUID.generate)
    __table_args__ = (UniqueConstraint("slug", "group_id", name="tags_slug_group_id_key"),)

    # ID Relationships
    group_id = Column(GUID, ForeignKey("groups.id"), nullable=False)
    group = orm.relationship("Group", back_populates="tools", foreign_keys=[group_id])

    name = Column(String, index=True, unique=True, nullable=False)
    slug = Column(String, index=True, unique=True, nullable=False)
    on_hand = Column(Boolean, default=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes_to_tools, back_populates="tools")

    @auto_init()
    def __init__(self, name, **_) -> None:
        self.slug = slugify(name)
