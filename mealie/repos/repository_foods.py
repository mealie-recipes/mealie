from pydantic import UUID4
from sqlalchemy import select, update

from mealie.db.models.household.shopping_list import ShoppingListItem
from mealie.db.models.recipe.ingredient import IngredientFoodModel
from mealie.schema.recipe.recipe_ingredient import IngredientFood

from .repository_generic import GroupRepositoryGeneric


class RepositoryFood(GroupRepositoryGeneric[IngredientFood, IngredientFoodModel]):
    def _get_food(self, id: UUID4) -> IngredientFoodModel:
        stmt = select(self.model).filter_by(**self._filter_builder(**{"id": id}))
        return self.session.execute(stmt).scalars().one()

    def merge(self, from_food: UUID4, to_food: UUID4) -> IngredientFood | None:
        from_model = self._get_food(from_food)
        to_model = self._get_food(to_food)

        to_model.ingredients += from_model.ingredients

        # Shopping list items reference the food directly rather than through the ingredients
        # relationship, so they have to be repointed explicitly. Without this the delete below
        # either violates a foreign key constraint or leaves the item pointing at a missing food.
        self.session.execute(
            update(ShoppingListItem).where(ShoppingListItem.food_id == from_food).values(food_id=to_food)
        )

        try:
            self.session.delete(from_model)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

        return self.get_one(to_food)
