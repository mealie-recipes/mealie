from collections.abc import Iterable

from pydantic import UUID4
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload

from mealie.db.models.household.shopping_list import ShoppingListItem
from mealie.db.models.recipe.ingredient import IngredientFoodModel, RecipeIngredientSubstitutionModel
from mealie.schema.recipe.recipe_ingredient import IngredientFood

from .repository_generic import GroupRepositoryGeneric


class RepositoryFood(GroupRepositoryGeneric[IngredientFood, IngredientFoodModel]):
    def _preserve_references(self, food: IngredientFoodModel) -> None:
        from mealie.schema.recipe.recipe_ingredient import FoodSnapshot

        snapshot = FoodSnapshot(
            source_id=food.id,
            name=food.name or "",
            plural_name=food.plural_name,
            description=food.description,
            extras={extra.key_name: extra.value for extra in food.extras},
        ).model_dump(mode="json")
        for ingredient in list(food.ingredients):
            # Food-level substitutions would otherwise vanish with the shared food.
            if not ingredient.substitutions:
                for substitution in food.substitutions:
                    name = substitution.substitute_food.name if substitution.substitute_food else ""
                    note = " ".join(part for part in (name, substitution.note) if part)
                    if note:
                        ingredient.substitutions.append(RecipeIngredientSubstitutionModel(note=note))
            ingredient.food_snapshot = snapshot.copy()
            ingredient.food = None
            ingredient.food_id = None

        items = self.session.scalars(select(ShoppingListItem).where(ShoppingListItem.food_id == food.id)).all()
        for item in items:
            item.food_snapshot = snapshot.copy()
            if item.label_id is None:
                item.label_id = food.label_id
            item.food = None
            item.food_id = None

        # Keep incoming substitutions as the already-supported note-only form.
        # Update the FK without removing from delete-orphan collections, then reload
        # those collections before deleting the food so preserved rows aren't cascaded.
        for relation in ("substitution_references", "recipe_substitution_references"):
            for substitution in list(getattr(food, relation)):
                substitution.note = " ".join(part for part in (food.name, substitution.note) if part)
                substitution.substitute_food_id = None
            self.session.flush()
            self.session.expire(food, [relation])

    def _delete_foods(self, foods: list[IngredientFoodModel]) -> list[IngredientFood]:
        try:
            result = [self.schema.model_validate(food) for food in foods]
            for food in foods:
                self._preserve_references(food)
            self.session.flush()
            for food in foods:
                self.session.delete(food)
            self.session.commit()
            return result
        except Exception:
            self.session.rollback()
            raise

    def delete(self, value, match_key: str | None = None) -> IngredientFood:
        food = self._query_one(value, match_key or self.primary_key)
        self.session.execute(select(self.model.id).where(self.model.id == food.id).with_for_update())
        return self._delete_foods([food])[0]

    def delete_many(self, values: Iterable) -> list[IngredientFood]:
        query = self._query(with_options=False).filter(self.model.id.in_(values)).filter_by(**self._filter_builder())
        foods = list(self.session.execute(query.order_by(self.model.id).with_for_update()).unique().scalars().all())
        return self._delete_foods(foods)

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
