from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.orm import Mapped, mapped_column

from .._model_base import BaseMixins, SqlAlchemyBase
from .._model_utils.auto_init import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from .recipe import RecipeModel


class RecipeTranslationModel(SqlAlchemyBase, BaseMixins):
    """
    A language overlay for a recipe. Holds only translated free-text; all structure
    (quantities, units, foods, references) stays on the canonical recipe.
    """

    __tablename__ = "recipe_translations"
    __table_args__ = (sa.UniqueConstraint("recipe_id", "locale", name="recipe_translations_recipe_id_locale_key"),)

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    recipe_id: Mapped[GUID] = mapped_column(GUID, sa.ForeignKey("recipes.id"), nullable=False, index=True)
    recipe: Mapped["RecipeModel"] = orm.relationship("RecipeModel", back_populates="translations")

    locale: Mapped[str] = mapped_column(sa.String, nullable=False, index=True)

    name: Mapped[str | None] = mapped_column(sa.String)
    description: Mapped[str | None] = mapped_column(sa.String)
    recipe_yield: Mapped[str | None] = mapped_column(sa.String)

    # Hash of the source strings at translation time; a mismatch on read means the translation is stale.
    source_hash: Mapped[str | None] = mapped_column(sa.String)

    instructions: Mapped[list["RecipeInstructionTranslationModel"]] = orm.relationship(
        "RecipeInstructionTranslationModel", cascade="all, delete-orphan"
    )
    ingredients: Mapped[list["RecipeIngredientTranslationModel"]] = orm.relationship(
        "RecipeIngredientTranslationModel", cascade="all, delete-orphan"
    )
    notes: Mapped[list["RecipeNoteTranslationModel"]] = orm.relationship(
        "RecipeNoteTranslationModel", cascade="all, delete-orphan"
    )

    @auto_init()
    def __init__(self, session, instructions=None, ingredients=None, notes=None, **_) -> None:
        self.instructions = [RecipeInstructionTranslationModel(**i, session=session) for i in (instructions or [])]
        self.ingredients = [RecipeIngredientTranslationModel(**i, session=session) for i in (ingredients or [])]
        self.notes = [RecipeNoteTranslationModel(**n, session=session) for n in (notes or [])]


class RecipeInstructionTranslationModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_instruction_translations"
    __table_args__ = (
        sa.UniqueConstraint(
            "translation_id", "instruction_id", name="recipe_instruction_translations_translation_id_instruction_id_key"
        ),
    )

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    translation_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("recipe_translations.id"), nullable=False, index=True
    )
    instruction_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("recipe_instructions.id"), nullable=False, index=True
    )

    title: Mapped[str | None] = mapped_column(sa.String)
    text: Mapped[str | None] = mapped_column(sa.String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class RecipeIngredientTranslationModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_ingredient_translations"
    __table_args__ = (
        sa.UniqueConstraint(
            "translation_id", "ingredient_id", name="recipe_ingredient_translations_translation_id_ingredient_id_key"
        ),
    )

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    translation_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("recipe_translations.id"), nullable=False, index=True
    )
    # Keyed by the ingredient's stable reference_id (not its integer PK), which survives recipe edits.
    ingredient_id: Mapped[GUID] = mapped_column(GUID, nullable=False, index=True)

    note: Mapped[str | None] = mapped_column(sa.String)
    original_text: Mapped[str | None] = mapped_column(sa.String)
    # Per-locale display overlay for the shared food/unit names; the canonical catalog entities stay untouched.
    food_name: Mapped[str | None] = mapped_column(sa.String)
    unit_name: Mapped[str | None] = mapped_column(sa.String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class RecipeNoteTranslationModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipe_note_translations"
    __table_args__ = (
        sa.UniqueConstraint(
            "translation_id", "note_index", name="recipe_note_translations_translation_id_note_index_key"
        ),
    )

    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)
    translation_id: Mapped[GUID] = mapped_column(
        GUID, sa.ForeignKey("recipe_translations.id"), nullable=False, index=True
    )
    # Notes have no stable id (integer PK, rebuilt on save), so overlay them by position within the recipe.
    note_index: Mapped[int] = mapped_column(sa.Integer, nullable=False)

    title: Mapped[str | None] = mapped_column(sa.String)
    text: Mapped[str | None] = mapped_column(sa.String)

    @auto_init()
    def __init__(self, **_) -> None:
        pass
