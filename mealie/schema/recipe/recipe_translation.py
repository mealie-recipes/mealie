from __future__ import annotations

import datetime

from pydantic import UUID4, ConfigDict, field_validator
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.lang.locale_config import LOCALE_CONFIG
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import UpdatedAtField


def validate_locale(locale: str) -> str:
    if locale not in LOCALE_CONFIG:
        raise ValueError(f"Unsupported locale '{locale}'")
    return locale


class RecipeTranslationRequest(MealieModel):
    locale: str

    _validate_locale = field_validator("locale")(validate_locale)


class InstructionTranslation(MealieModel):
    instruction_id: UUID4
    title: str | None = None
    text: str | None = None
    model_config = ConfigDict(from_attributes=True)


class IngredientTranslation(MealieModel):
    ingredient_id: UUID4
    note: str | None = None
    original_text: str | None = None
    model_config = ConfigDict(from_attributes=True)


class NoteTranslation(MealieModel):
    note_index: int
    title: str | None = None
    text: str | None = None
    model_config = ConfigDict(from_attributes=True)


class RecipeTranslationSummary(MealieModel):
    """A lightweight entry for the recipe-page language switcher."""

    locale: str
    name: str | None = None
    is_stale: bool = False
    updated_at: datetime.datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)


class RecipeTranslation(MealieModel):
    locale: str
    name: str | None = None
    description: str | None = None
    recipe_yield: str | None = None
    source_hash: str | None = None
    is_stale: bool = False

    instructions: list[InstructionTranslation] = []
    ingredients: list[IngredientTranslation] = []
    notes: list[NoteTranslation] = []

    created_at: datetime.datetime | None = None
    updated_at: datetime.datetime | None = UpdatedAtField(None)
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        from mealie.db.models.recipe.translation import RecipeTranslationModel

        return [
            selectinload(RecipeTranslationModel.instructions),
            selectinload(RecipeTranslationModel.ingredients),
            selectinload(RecipeTranslationModel.notes),
        ]
