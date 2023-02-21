from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, event, orm
from sqlalchemy.orm import Mapped, mapped_column
from text_unidecode import unidecode

from mealie.db.models._model_base import BaseMixins, SqlAlchemyBase
from mealie.db.models.labels import MultiPurposeLabel
from mealie.db.models.recipe.api_extras import IngredientFoodExtras, api_extras

from .._model_utils import auto_init
from .._model_utils.guid import GUID

if TYPE_CHECKING:
    from ..group import Group


class IngredientUnitModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_units"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="ingredient_units", foreign_keys=[group_id])

    name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    abbreviation: Mapped[str | None] = mapped_column(String)
    use_abbreviation: Mapped[bool | None] = mapped_column(Boolean, default=False)
    fraction: Mapped[bool | None] = mapped_column(Boolean, default=True)
    ingredients: Mapped[list["RecipeIngredient"]] = orm.relationship("RecipeIngredient", back_populates="unit")

    @auto_init()
    def __init__(self, **_) -> None:
        pass


class IngredientFoodModel(SqlAlchemyBase, BaseMixins):
    __tablename__ = "ingredient_foods"
    id: Mapped[GUID] = mapped_column(GUID, primary_key=True, default=GUID.generate)

    # ID Relationships
    group_id: Mapped[GUID] = mapped_column(GUID, ForeignKey("groups.id"), nullable=False, index=True)
    group: Mapped["Group"] = orm.relationship("Group", back_populates="ingredient_foods", foreign_keys=[group_id])

    name: Mapped[str | None] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String)
    ingredients: Mapped[list["RecipeIngredient"]] = orm.relationship("RecipeIngredient", back_populates="food")
    extras: Mapped[list[IngredientFoodExtras]] = orm.relationship("IngredientFoodExtras", cascade="all, delete-orphan")

    label_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("multi_purpose_labels.id"), index=True)
    label: Mapped[MultiPurposeLabel | None] = orm.relationship(MultiPurposeLabel, uselist=False, back_populates="foods")

    @api_extras
    @auto_init()
    def __init__(self, **_) -> None:
        pass


class RecipeIngredient(SqlAlchemyBase, BaseMixins):
    __tablename__ = "recipes_ingredients"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    position: Mapped[int | None] = mapped_column(Integer, index=True)
    recipe_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("recipes.id"))

    title: Mapped[str | None] = mapped_column(String)  # Section Header - Shows if Present
    note: Mapped[str | None] = mapped_column(String)  # Force Show Text - Overrides Concat

    # Scaling Items
    unit_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_units.id"), index=True)
    unit: Mapped[IngredientUnitModel | None] = orm.relationship(IngredientUnitModel, uselist=False)

    food_id: Mapped[GUID | None] = mapped_column(GUID, ForeignKey("ingredient_foods.id"), index=True)
    food: Mapped[IngredientFoodModel | None] = orm.relationship(IngredientFoodModel, uselist=False)
    quantity: Mapped[float | None] = mapped_column(Float)

    original_text: Mapped[str | None] = mapped_column(String)

    reference_id: Mapped[GUID | None] = mapped_column(GUID)  # Reference Links

    # Automatically updated by sqlalchemy event, do not write to this manually
    note_normalized: Mapped[str | None] = mapped_column(String, index=True)
    original_text_normalized: Mapped[str | None] = mapped_column(String, index=True)

    @auto_init()
    def __init__(self, note: str | None = None, orginal_text: str | None = None, **_) -> None:
        # SQLAlchemy events do not seem to register things that are set during auto_init
        if note is not None:
            self.note_normalized = unidecode(note).lower().strip()

        if orginal_text is not None:
            self.orginal_text = unidecode(orginal_text).lower().strip()


@event.listens_for(RecipeIngredient.note, "set")
def receive_note(target: RecipeIngredient, value: str, oldvalue, initiator):
    if value is not None:
        target.name_normalized = unidecode(value).lower().strip()
    else:
        target.name_normalized = None


@event.listens_for(RecipeIngredient.original_text, "set")
def receive_original_text(target: RecipeIngredient, value: str, oldvalue, initiator):
    if value is not None:
        target.original_text_normalized = unidecode(value).lower().strip()
    else:
        target.original_text_normalized = None
