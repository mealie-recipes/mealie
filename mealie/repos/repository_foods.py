from pydantic import UUID4

from mealie.db.models.recipe.ingredient import IngredientFoodModel
from mealie.schema.recipe.recipe_ingredient import IngredientFood

from .repository_generic import RepositoryGeneric


class RepositoryFood(RepositoryGeneric[IngredientFood, IngredientFoodModel]):
    def merge(self, from_food: UUID4, to_food: UUID4) -> IngredientFood | None:

        from_model: IngredientFoodModel = (
            self.session.query(self.sql_model).filter_by(**self._filter_builder(**{"id": from_food})).one()
        )

        to_model: IngredientFoodModel = (
            self.session.query(self.sql_model).filter_by(**self._filter_builder(**{"id": to_food})).one()
        )

        to_model.ingredients += from_model.ingredients

        try:
            self.session.delete(from_model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return self.get_one(to_food)

    def by_group(self, group_id: UUID4) -> "RepositoryFood":
        return super().by_group(group_id)  # type: ignore
