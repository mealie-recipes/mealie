from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, orm

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models._model_utils import auto_init

recipes_to_tools = Table(
    "recipes_to_tools",
    SqlAlchemyBase.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("tool_id", Integer, ForeignKey("tools.id")),
)


class Tool(SqlAlchemyBase, BaseMixins):
    __tablename__ = "tools"
    name = Column(String, index=True, unique=True, nullable=False)
    on_hand = Column(Boolean, default=False)
    recipes = orm.relationship("RecipeModel", secondary=recipes_to_tools, back_populates="tools")

    @auto_init()
    def __init__(self, name, on_hand, **_) -> None:
        self.on_hand = on_hand
        self.name = name
