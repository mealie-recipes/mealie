from __future__ import annotations

import hashlib
from uuid import UUID

from mealie.schema.recipe.recipe import Recipe
from mealie.schema.recipe.recipe_translation import (
    IngredientTranslation,
    InstructionTranslation,
    NoteTranslation,
    RecipeTranslation,
    RecipeTranslationSummary,
)


def source_hash(recipe: Recipe) -> str:
    """
    Stable digest over exactly the strings a translation covers, in id order.

    Used to detect staleness: if the original recipe's translatable text changes, the stored hash no longer
    matches and the translation is flagged outdated. This covers the food and unit *names* (which are now
    translated for display) but not quantities, so rescaling an ingredient does not needlessly invalidate a
    translation.
    """

    parts: list[str] = [recipe.name or "", recipe.description or "", recipe.recipe_yield or ""]

    for step in recipe.recipe_instructions or []:
        parts.append(f"i:{step.id}:{step.title or ''}:{step.text or ''}")

    for ingredient in recipe.recipe_ingredient or []:
        food_name = ingredient.food.name if ingredient.food else ""
        unit_name = ingredient.unit.name if ingredient.unit else ""
        parts.append(
            f"g:{ingredient.reference_id}:{ingredient.note or ''}:{ingredient.original_text or ''}"
            f":{food_name or ''}:{unit_name or ''}"
        )

    for index, note in enumerate(recipe.notes or []):
        parts.append(f"n:{index}:{note.title or ''}:{note.text or ''}")

    joined = "\x1f".join(parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def is_translation_stale(recipe: Recipe, translation_source_hash: str | None) -> bool:
    return translation_source_hash != source_hash(recipe)


def summarize_translations(recipe: Recipe, translations: list[RecipeTranslation]) -> list[RecipeTranslationSummary]:
    current = source_hash(recipe)
    return [
        RecipeTranslationSummary(
            locale=t.locale,
            name=t.name,
            is_stale=t.source_hash != current,
            updated_at=t.updated_at,
        )
        for t in translations
    ]


def apply_translation(recipe: Recipe, translation: RecipeTranslation) -> Recipe:
    """
    Return a copy of ``recipe`` with translated free-text substituted onto matching steps/ingredients/notes.

    Only text is touched — quantities, units, foods, reference ids and ingredient references are left untouched.
    Any key without a translation falls back to the original string, so a partial translation degrades
    gracefully rather than blanking fields.
    """

    translated = recipe.model_copy(deep=True)

    translated.name = translation.name or translated.name
    translated.description = translation.description if translation.description is not None else translated.description
    translated.recipe_yield = translation.recipe_yield or translated.recipe_yield

    step_map: dict[UUID, InstructionTranslation] = {t.instruction_id: t for t in translation.instructions}
    for step in translated.recipe_instructions or []:
        if (t := step_map.get(step.id)) is not None:
            if t.title is not None:
                step.title = t.title
            if t.text is not None:
                step.text = t.text

    ingredient_map: dict[UUID, IngredientTranslation] = {t.ingredient_id: t for t in translation.ingredients}
    for ingredient in translated.recipe_ingredient or []:
        if (t := ingredient_map.get(ingredient.reference_id)) is not None:
            if t.note is not None:
                ingredient.note = t.note
            if t.original_text is not None:
                ingredient.original_text = t.original_text
            # Overlay the shared food/unit names onto this per-locale copy only; the catalog entities are untouched.
            if t.food_name and ingredient.food is not None:
                ingredient.food.name = t.food_name
                ingredient.food.plural_name = t.food_name
            if t.unit_name and ingredient.unit is not None:
                ingredient.unit.name = t.unit_name
                ingredient.unit.plural_name = t.unit_name
                # Prefer the translated spelled-out name over the original abbreviation for display.
                ingredient.unit.use_abbreviation = False

    note_map: dict[int, NoteTranslation] = {t.note_index: t for t in translation.notes}
    for index, note in enumerate(translated.notes or []):
        if (t := note_map.get(index)) is not None:
            if t.title is not None:
                note.title = t.title
            if t.text is not None:
                note.text = t.text

    translated.translated_locale = translation.locale
    return translated
