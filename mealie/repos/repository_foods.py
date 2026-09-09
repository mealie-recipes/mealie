from pydantic import UUID4
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from mealie.db.models.household.shopping_list import ShoppingListItem
from mealie.db.models.recipe.ingredient import IngredientFoodModel, RecipeIngredientSubstitutionModel
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

    def _merge_recipe_substitutions(self, from_food: UUID4, to_food: UUID4) -> None:
        """
        Repoints the recipe-tier substitutions aimed at the merged-away food.

        These rows hang off ingredient lines rather than off the food, so moving the ingredients
        does not carry them along; left alone they are cascade-deleted with the food, dropping
        substitutions the recipes still want. Rows that would become self-referential or
        duplicate once the two foods are one are deleted instead, since that is what they say.
        """

        # both ids are matched, so this reads the same whether or not the ingredient move has
        # been flushed yet: either way those ingredients end up calling for the target
        merged_food_ids = [from_food, to_food]
        stmt = (
            select(RecipeIngredientSubstitutionModel)
            .filter(RecipeIngredientSubstitutionModel.substitute_food_id.in_(merged_food_ids))
            .options(joinedload(RecipeIngredientSubstitutionModel.ingredient))
            .order_by(
                RecipeIngredientSubstitutionModel.ingredient_id,
                RecipeIngredientSubstitutionModel.position,
            )
        )

        # the recipe tier has no unique constraint to lean on, so duplicates are collapsed here,
        # keeping the first the same way the schema does when it prunes a payload
        repointed_ingredient_ids: set[int] = set()
        repointed_rows: list[RecipeIngredientSubstitutionModel] = []
        for row in self.session.execute(stmt).unique().scalars().all():
            if row.ingredient.food_id in merged_food_ids or row.ingredient_id in repointed_ingredient_ids:
                self.session.delete(row)
                continue

            repointed_ingredient_ids.add(row.ingredient_id)
            row.substitute_food_id = to_food
            repointed_rows.append(row)

        # the session doesn't autoflush, and deleting the food actively loads its substitution rows
        # to cascade over them, so an unwritten repoint is read back off the database still pointing
        # at the old food and deleted with it. Only these rows are written: a full flush would also
        # write the ingredient move, which the delete then undoes by clearing their food.
        if repointed_rows:
            self.session.flush(repointed_rows)

    def merge(self, from_food: UUID4, to_food: UUID4) -> IngredientFood | None:
        from_model = self._get_food(from_food)
        to_model = self._get_food(to_food)

        to_model.ingredients += from_model.ingredients
        self._merge_substitutions(from_model, to_model)
        self._merge_recipe_substitutions(from_food, to_food)

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
