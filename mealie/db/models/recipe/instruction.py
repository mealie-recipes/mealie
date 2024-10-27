from pydantic import ConfigDict
from sqlalchemy import ForeignKey, Integer, String, orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID


class RecipeIngredientRefLink(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_ingredient_ref_link"
    instruction_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipe_instructions.id"), index=True)
    reference_id: Mapped[GUID | None] = mapped_column(GUID, index=True)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class RecipeInstruction(SqlAlchemyBase):
    __tablename__ = "recipe_instructions"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"), index=True)
    position: Mapped[int | None] = mapped_column(Integer, index=True)
    type: Mapped[str | None] = mapped_column(String, default="")
    title: Mapped[str | None] = mapped_column(String)  # This is the section title!!!
    text: Mapped[str | None] = mapped_column(String, index=True)
    summary: Mapped[str | None] = mapped_column(String)

    ingredient_references: Mapped[list[RecipeIngredientRefLink]] = orm.relationship(
        RecipeIngredientRefLink, cascade="all, delete-orphan"
    )
    model_config = ConfigDict(
        exclude={
            "id",
            "ingredient_references",
        }
    )

    @auto_init()
    def __init__(self, ingredient_references, session, **_) -> None:
        self.ingredient_references = [RecipeIngredientRefLink(**ref, session=session) for ref in ingredient_references]
