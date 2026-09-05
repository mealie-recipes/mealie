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

    def _merge_substitutions(self, from_model: IngredientFoodModel, to_model: IngredientFoodModel) -> None:
        """
        Moves both directions of the merged-away food's substitutions onto the target.

        Left alone these are cascade-deleted with the food, silently dropping substitutions
        the user never touched. Substitutions that would become self-referential or duplicate once
        the two foods are one are deliberately left behind to go with it.
        """

        to_food = to_model.id

        # both sides are read up front, so the sets aren't invalidated as rows are moved
        existing_substitute_ids = {row.substitute_food_id for row in to_model.substitutions if row.substitute_food_id}
        existing_source_ids = {row.food_id for row in to_model.substitution_references}
        outbound = list(from_model.substitutions)
        inbound = list(from_model.substitution_references)

        for row in outbound:
            if row.substitute_food_id is not None:
                # `from -> to` becomes a self-substitution once the foods are one, and
                # `from -> S` duplicates an existing `to -> S`
                if row.substitute_food_id == to_food or row.substitute_food_id in existing_substitute_ids:
                    continue

                existing_substitute_ids.add(row.substitute_food_id)

            # note-only substitutions carry no food reference and always survive the merge
            to_model.substitutions.append(row)

        for row in inbound:
            # `to -> from` is the mirror self-substitution, and `X -> from` duplicates an `X -> to`
            if row.food_id == to_food or row.food_id in existing_source_ids:
                continue

            existing_source_ids.add(row.food_id)
            to_model.substitution_references.append(row)

    def merge(self, from_food: UUID4, to_food: UUID4) -> IngredientFood | None:
        from_model = self._get_food(from_food)
        to_model = self._get_food(to_food)

        to_model.ingredients += from_model.ingredients
        self._merge_substitutions(from_model, to_model)

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
