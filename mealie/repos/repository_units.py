from pydantic import UUID4
from sqlalchemy import select

from mealie.db.models.recipe.ingredient import IngredientUnitModel
from mealie.schema.recipe.recipe_ingredient import IngredientUnit

from .repository_generic import GroupRepositoryGeneric


class RepositoryUnit(GroupRepositoryGeneric[IngredientUnit, IngredientUnitModel]):
    def _get_unit(self, id: UUID4) -> IngredientUnitModel:
        stmt = select(self.model).filter_by(**self._filter_builder(**{"id": id}))
        return self.session.execute(stmt).scalars().one()

    def merge(self, from_unit: UUID4, to_unit: UUID4) -> IngredientUnit | None:
        from_model = self._get_unit(from_unit)
        to_model = self._get_unit(to_unit)

        to_model.ingredients += from_model.ingredients

        try:
            self.session.delete(from_model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return self.get_one(to_unit)
