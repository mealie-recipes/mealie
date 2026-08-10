from uuid import UUID

import sqlalchemy as sa
from pydantic import UUID4
from sqlalchemy.orm import Session

from mealie.db.models.recipe.translation import RecipeTranslationModel
from mealie.schema.recipe.recipe_translation import RecipeTranslation


class RepositoryRecipeTranslations:
    """
    Bespoke access for recipe language overlays.

    Overlays are written wholesale (delete-and-recreate per locale) rather than diffed, so this deliberately
    does not extend the generic CRUD repository.
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    def _query(self):
        return sa.select(RecipeTranslationModel).options(*RecipeTranslation.loader_options())

    def get_for_recipe(self, recipe_id: UUID4 | str) -> list[RecipeTranslation]:
        rows = (
            self.session.execute(self._query().where(RecipeTranslationModel.recipe_id == recipe_id))
            .unique()
            .scalars()
            .all()
        )
        return [RecipeTranslation.model_validate(row) for row in rows]

    def get_one(self, recipe_id: UUID4 | str, locale: str) -> RecipeTranslation | None:
        row = (
            self.session.execute(
                self._query().where(
                    RecipeTranslationModel.recipe_id == recipe_id,
                    RecipeTranslationModel.locale == locale,
                )
            )
            .unique()
            .scalars()
            .one_or_none()
        )
        return RecipeTranslation.model_validate(row) if row else None

    def upsert(self, recipe_id: UUID4 | str, translation: RecipeTranslation) -> RecipeTranslation:
        """Replace any existing overlay for this (recipe, locale) with the given translation."""
        self._delete_row(recipe_id, translation.locale)

        row = RecipeTranslationModel(
            session=self.session,
            recipe_id=recipe_id if isinstance(recipe_id, UUID) else UUID(str(recipe_id)),
            locale=translation.locale,
            name=translation.name,
            description=translation.description,
            recipe_yield=translation.recipe_yield,
            source_hash=translation.source_hash,
            instructions=[
                {"instruction_id": i.instruction_id, "title": i.title, "text": i.text} for i in translation.instructions
            ],
            ingredients=[
                {
                    "ingredient_id": i.ingredient_id,
                    "note": i.note,
                    "original_text": i.original_text,
                    "food_name": i.food_name,
                    "unit_name": i.unit_name,
                }
                for i in translation.ingredients
            ],
            notes=[{"note_index": n.note_index, "title": n.title, "text": n.text} for n in translation.notes],
        )
        self.session.add(row)
        self.session.commit()
        self.session.refresh(row)
        return RecipeTranslation.model_validate(row)

    def delete(self, recipe_id: UUID4 | str, locale: str) -> bool:
        deleted = self._delete_row(recipe_id, locale)
        self.session.commit()
        return deleted

    def _delete_row(self, recipe_id: UUID4 | str, locale: str) -> bool:
        existing = (
            self.session.execute(
                sa.select(RecipeTranslationModel).where(
                    RecipeTranslationModel.recipe_id == recipe_id,
                    RecipeTranslationModel.locale == locale,
                )
            )
            .unique()
            .scalars()
            .one_or_none()
        )
        if existing is None:
            return False

        self.session.delete(existing)
        self.session.flush()
        return True
