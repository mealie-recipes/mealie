from pydantic import UUID4

from mealie.db.models.recipe.ingredient import IngredientUnitModel
from mealie.schema.recipe.recipe_ingredient import IngredientUnit

from .repository_generic import RepositoryGeneric


class RepositoryUnit(RepositoryGeneric[IngredientUnit, IngredientUnitModel]):
    def merge(self, from_unit: UUID4, to_unit: UUID4) -> IngredientUnit | None:

        from_model: IngredientUnitModel = (
            self.session.query(self.sql_model).filter_by(**self._filter_builder(**{"id": from_unit})).one()
        )

        to_model: IngredientUnitModel = (
            self.session.query(self.sql_model).filter_by(**self._filter_builder(**{"id": to_unit})).one()
        )

        to_model.ingredients += from_model.ingredients

        try:
            self.session.delete(from_model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return self.get_one(to_unit)

    def by_group(self, group_id: UUID4) -> "RepositoryUnit":
        return super().by_group(group_id)  # type: ignore
