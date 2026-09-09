from collections.abc import Sequence

from pydantic import UUID4
from sqlalchemy import func, select
from sqlalchemy.orm import with_expression

from mealie.db.models.household.shopping_list import ShoppingListItem
from mealie.db.models.recipe.ingredient import IngredientFoodModel, RecipeIngredientModel
from mealie.schema.recipe.recipe_ingredient import IngredientFood

from .repository_generic import GroupRepositoryGeneric


class RepositoryFood(GroupRepositoryGeneric[IngredientFood, IngredientFoodModel]):
    def _query(self, override_schema=None, with_options=True):
        q = super()._query(override_schema=override_schema, with_options=with_options)
        count_sq = (
            select(func.count(func.distinct(RecipeIngredientModel.recipe_id)))
            .where(RecipeIngredientModel.food_id == IngredientFoodModel.id)
            .correlate(IngredientFoodModel)
            .scalar_subquery()
        )
        return q.options(with_expression(IngredientFoodModel.recipe_count, count_sq))

    def _get_food(self, id: UUID4) -> IngredientFoodModel:
        stmt = select(self.model).filter_by(**self._filter_builder(**{"id": id}))
        return self.session.execute(stmt).scalars().one()

    def get_empty(self) -> Sequence[IngredientFoodModel]:
        # a food is only "unused" if it's absent from both recipe ingredients and
        # shopping list items; IngredientFoodModel has no ORM relationship to
        # ShoppingListItem, so we check the latter via an EXISTS subquery
        used_in_shopping_lists = (
            select(ShoppingListItem.id)
            .where(ShoppingListItem.food_id == IngredientFoodModel.id)
            .correlate(IngredientFoodModel)
            .exists()
        )
        stmt = select(IngredientFoodModel).filter(~IngredientFoodModel.ingredients.any(), ~used_in_shopping_lists)
        return self.session.execute(stmt).scalars().all()

    def merge(self, from_food: UUID4, to_food: UUID4) -> IngredientFood | None:
        from_model = self._get_food(from_food)
        to_model = self._get_food(to_food)

        to_model.ingredients += from_model.ingredients

        try:
            self.session.delete(from_model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return self.get_one(to_food)
