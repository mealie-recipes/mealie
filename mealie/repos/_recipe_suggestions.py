import logging
from typing import TYPE_CHECKING, Any, cast

import sqlalchemy as sa
from fastapi import HTTPException
from pydantic import UUID4
from sqlalchemy import orm
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe.ingredient import (
    IngredientFoodModel,
    IngredientFoodSubstitutionModel,
    RecipeIngredientModel,
    RecipeIngredientSubstitutionModel,
    households_to_ingredient_foods,
)
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.recipe.tool import Tool, households_to_tools, recipes_to_tools
from mealie.db.models.users.users import User
from mealie.schema.recipe.recipe import RecipeSummary
from mealie.schema.recipe.recipe_ingredient import IngredientFood, IngredientFoodSummary
from mealie.schema.recipe.recipe_suggestion import (
    RecipeSuggestionQuery,
    RecipeSuggestionResponseItem,
    RecipeSuggestionSubstitutedFood,
)
from mealie.schema.recipe.recipe_tool import RecipeToolOut
from mealie.schema.response.pagination import RequestQuery
from mealie.services.query_filter.builder import QueryFilterBuilder

if TYPE_CHECKING:
    from sqlalchemy.orm.session import Session


class RecipeSuggestionMixin:
    """
    The recipe finder, mixed into RepositoryRecipes.

    Split out because it is close to half of what that module would otherwise be, and the
    only part of it that is not ordinary CRUD and search. It owns no state; everything it
    reads belongs to the repository it is mixed into, and is declared below.

    Those declarations are type-checking only, so they add no class attributes and cannot
    shadow the real implementations through the MRO at runtime.
    """

    if TYPE_CHECKING:
        model: type[RecipeModel]
        session: Session
        logger: logging.Logger
        user_id: UUID4 | None
        group_id: UUID4 | None
        household_id: UUID4 | None

        def _filter_builder(self, **kwargs) -> dict[str, Any]: ...

        def _log_exception(self, e: Exception) -> None: ...

        def add_order_by_to_query(self, query: sa.Select, request_query: RequestQuery) -> sa.Select: ...

    @staticmethod
    def _find_substitute_on_hand(
        ingredient: RecipeIngredientModel, food: IngredientFoodModel, on_hand_food_ids: set[UUID4]
    ) -> IngredientFoodModel | None:
        """
        The first substitute food the user has on hand, or None.

        Recipe-level substitutions are checked before the food's own, since they were written
        about this recipe specifically. A note-only substitution has no food id, and `None` is
        never in the on-hand set, so it can never satisfy an ingredient.
        """

        for substitution in [*ingredient.substitutions, *food.substitutions]:
            if substitution.substitute_food_id in on_hand_food_ids:
                return substitution.substitute_food

        return None

    @staticmethod
    def _covered_by_substitution(ingredients_alias, food_ids: list[UUID4]):
        """
        Whether an ingredient can be covered by a substitution to one of `food_ids`.

        The substitution runs from the recipe's food to the user's: if the recipe calls for
        chicken stock and the user has chicken broth, the substitution that makes the recipe
        cookable is `stock -> broth`. Expanding the user's foods by what they can substitute
        for is the same query backwards, and quietly wrong.

        Both branches require a non-null substitute food. Note-only substitutions have no
        food to match against and can never satisfy an ingredient.
        """

        food_level = (
            sa.select(1)
            .where(
                IngredientFoodSubstitutionModel.food_id == ingredients_alias.food_id,
                IngredientFoodSubstitutionModel.substitute_food_id.isnot(None),
                IngredientFoodSubstitutionModel.substitute_food_id.in_(food_ids),
            )
            .correlate(ingredients_alias)
            .exists()
        )
        recipe_level = (
            sa.select(1)
            .where(
                RecipeIngredientSubstitutionModel.ingredient_id == ingredients_alias.id,
                RecipeIngredientSubstitutionModel.substitute_food_id.isnot(None),
                RecipeIngredientSubstitutionModel.substitute_food_id.in_(food_ids),
            )
            .correlate(ingredients_alias)
            .exists()
        )

        return sa.or_(food_level, recipe_level)

    def _with_on_hand_ids(
        self, params: RecipeSuggestionQuery, user_food_ids: list[UUID4], user_tool_ids: list[UUID4]
    ) -> tuple[list[UUID4], list[UUID4]]:
        """The user's ids, plus whatever their household already has on hand."""

        food_ids = user_food_ids.copy()
        tool_ids = user_tool_ids.copy()

        if params.include_foods_on_hand and self.user_id:
            foods_on_hand_query = (
                sa.select(households_to_ingredient_foods.c.food_id)
                .join(User, households_to_ingredient_foods.c.household_id == User.household_id)
                .filter(
                    sa.not_(households_to_ingredient_foods.c.food_id.in_(food_ids)),
                    User.id == self.user_id,
                )
            )
            food_ids.extend(self.session.execute(foods_on_hand_query).scalars().all())

        if params.include_tools_on_hand and self.user_id:
            tools_on_hand_query = (
                sa.select(households_to_tools.c.tool_id)
                .join(User, households_to_tools.c.household_id == User.household_id)
                .filter(
                    sa.not_(households_to_tools.c.tool_id.in_(tool_ids)),
                    User.id == self.user_id,
                )
            )
            tool_ids.extend(self.session.execute(tools_on_hand_query).scalars().all())

        return food_ids, tool_ids

    def _filter_suggestions_by_tools(
        self, q: sa.Select, params: RecipeSuggestionQuery, tools_alias, tool_ids_with_on_hand: list[UUID4]
    ) -> sa.Select:
        """Drops recipes missing too many tools, and orders by how many are missing."""

        unmatched_tools_query = (
            sa.select(recipes_to_tools.c.recipe_id, sa.func.count().label("unmatched_tools_count"))
            .join(tools_alias, recipes_to_tools.c.tool_id == tools_alias.id)
            .filter(sa.not_(tools_alias.id.in_(tool_ids_with_on_hand)))
            .group_by(recipes_to_tools.c.recipe_id)
            .subquery()
        )

        return (
            q.outerjoin(unmatched_tools_query, self.model.id == unmatched_tools_query.c.recipe_id)
            .filter(
                sa.or_(
                    unmatched_tools_query.c.unmatched_tools_count.is_(None),
                    unmatched_tools_query.c.unmatched_tools_count <= params.max_missing_tools,
                )
            )
            .order_by(unmatched_tools_query.c.unmatched_tools_count.asc().nulls_first())
        )

    def _filter_suggestions_by_foods(
        self,
        q: sa.Select,
        params: RecipeSuggestionQuery,
        settings_alias,
        ingredients_alias,
        user_food_ids: list[UUID4],
        food_ids_with_on_hand: list[UUID4],
    ) -> sa.Select:
        """
        Drops recipes missing too many foods, and orders by how many are missing.
        """

        unmatched_filter = sa.not_(ingredients_alias.food_id.in_(food_ids_with_on_hand))
        if params.include_substitutions:
            covered = self._covered_by_substitution(ingredients_alias, food_ids_with_on_hand)
            unmatched_filter = sa.and_(unmatched_filter, sa.not_(covered))

        unmatched_foods_query = (
            sa.select(ingredients_alias.recipe_id, sa.func.count().label("unmatched_foods_count"))
            .filter(unmatched_filter)
            .filter(ingredients_alias.food_id.isnot(None))
            .group_by(ingredients_alias.recipe_id)
            .subquery()
        )
        total_user_foods_query = (
            sa.select(ingredients_alias.recipe_id, sa.func.count().label("total_user_foods_count"))
            .filter(ingredients_alias.food_id.in_(user_food_ids))
            .group_by(ingredients_alias.recipe_id)
            .subquery()
        )
        substituted_user_foods_query = None
        if params.include_substitutions:
            substituted_user_foods_query = (
                sa.select(ingredients_alias.recipe_id, sa.func.count().label("substituted_user_foods_count"))
                .filter(ingredients_alias.food_id.isnot(None))
                .filter(sa.not_(ingredients_alias.food_id.in_(user_food_ids)))
                .filter(self._covered_by_substitution(ingredients_alias, user_food_ids))
                .group_by(ingredients_alias.recipe_id)
                .subquery()
            )

        q = (
            q.join(settings_alias, self.model.settings)
            .outerjoin(unmatched_foods_query, self.model.id == unmatched_foods_query.c.recipe_id)
            .outerjoin(total_user_foods_query, self.model.id == total_user_foods_query.c.recipe_id)
            .filter(
                sa.or_(
                    unmatched_foods_query.c.unmatched_foods_count.is_(None),
                    unmatched_foods_query.c.unmatched_foods_count <= params.max_missing_foods,
                ),
            )
            .order_by(
                unmatched_foods_query.c.unmatched_foods_count.asc().nulls_first(),
                # favor recipes with more matched foods, in case the user is looking for something specific
                total_user_foods_query.c.total_user_foods_count.desc().nulls_last(),
            )
        )

        # recipes cookable as written outrank recipes cookable with a swap
        at_least_one_match = [total_user_foods_query.c.total_user_foods_count > 0]
        if substituted_user_foods_query is not None:
            q = q.outerjoin(
                substituted_user_foods_query, self.model.id == substituted_user_foods_query.c.recipe_id
            ).order_by(substituted_user_foods_query.c.substituted_user_foods_count.desc().nulls_last())
            at_least_one_match.append(substituted_user_foods_query.c.substituted_user_foods_count > 0)

        # only include recipes that have at least one food in the user's list
        return q.filter(sa.or_(*at_least_one_match))

    @staticmethod
    def _suggestion_loader_options(params: RecipeSuggestionQuery, user_food_ids: list[UUID4]) -> list[LoaderOption]:
        options = list(RecipeSummary.loader_options())
        if not (user_food_ids and params.include_substitutions):
            return options

        # the suggestion builder walks each ingredient's substitutions and its food's; without
        # these the substitute lookup costs a lazy load per ingredient per recipe
        options.extend(
            [
                orm.selectinload(RecipeModel.recipe_ingredient)
                .selectinload(RecipeIngredientModel.substitutions)
                .joinedload(RecipeIngredientSubstitutionModel.substitute_food),
                orm.selectinload(RecipeModel.recipe_ingredient)
                .joinedload(RecipeIngredientModel.food)
                .selectinload(IngredientFoodModel.substitutions)
                .joinedload(IngredientFoodSubstitutionModel.substitute_food),
            ]
        )

        return options

    def _missing_and_substituted_foods(
        self, recipe: RecipeModel, params: RecipeSuggestionQuery, on_hand_food_ids: set[UUID4]
    ) -> tuple[list[IngredientFood], list[RecipeSuggestionSubstitutedFood]]:
        """
        Splits the recipe's foods the user lacks into the ones a substitute covers and the
        ones nothing covers, using the same satisfaction rule the query ranked on. Judged any
        other way, a food the query counted as covered gets reported back as missing.
        """

        missing_foods: list[IngredientFood] = []
        substituted_foods: list[RecipeSuggestionSubstitutedFood] = []

        seen_food_ids: set[UUID4] = set(on_hand_food_ids)
        for ingredient in recipe.recipe_ingredient:
            if not ingredient.food:
                continue
            if ingredient.food.id in seen_food_ids:
                continue

            seen_food_ids.add(ingredient.food.id)

            substitute = (
                self._find_substitute_on_hand(ingredient, ingredient.food, on_hand_food_ids)
                if params.include_substitutions
                else None
            )
            if substitute:
                substituted_foods.append(
                    RecipeSuggestionSubstitutedFood(
                        food=IngredientFood.model_validate(ingredient.food),
                        substitute_food=IngredientFoodSummary.model_validate(substitute),
                    )
                )
            else:
                missing_foods.append(IngredientFood.model_validate(ingredient.food))

        return missing_foods, substituted_foods

    @staticmethod
    def _missing_tools(recipe: RecipeModel, on_hand_tool_ids: set[UUID4]) -> list[RecipeToolOut]:
        missing_tools: list[RecipeToolOut] = []

        seen_tool_ids: set[UUID4] = set(on_hand_tool_ids)
        for tool in recipe.tools:
            if tool.id in seen_tool_ids:
                continue

            seen_tool_ids.add(tool.id)
            missing_tools.append(RecipeToolOut.model_validate(tool))

        return missing_tools

    def find_suggested_recipes(
        self,
        params: RecipeSuggestionQuery,
        food_ids: list[UUID4] | None = None,
        tool_ids: list[UUID4] | None = None,
    ) -> list[RecipeSuggestionResponseItem]:
        """
        Queries all recipes and returns the ones that are missing the least amount of foods and tools.

        Results are ordered first by number of missing tools, then foods, and finally by the user-specified order.
        If foods are provided, the query will prefer recipes with more matches to user-provided foods.
        """

        if not params.order_by:
            params.order_by = "created_at"

        user_food_ids = list(set(food_ids or []))
        user_tool_ids = list(set(tool_ids or []))
        food_ids_with_on_hand, tool_ids_with_on_hand = self._with_on_hand_ids(params, user_food_ids, user_tool_ids)

        ## Build suggestion query
        settings_alias = orm.aliased(RecipeSettings)
        ingredients_alias = orm.aliased(RecipeIngredientModel)
        tools_alias = orm.aliased(Tool)

        q = sa.select(self.model).filter(self.model.household_id.is_not(None))
        fltr = self._filter_builder()
        q = q.filter_by(**fltr)

        # Tools goes first so we can order by missing tools count before foods
        if user_tool_ids:
            q = self._filter_suggestions_by_tools(q, params, tools_alias, tool_ids_with_on_hand)

        if user_food_ids:
            q = self._filter_suggestions_by_foods(
                q, params, settings_alias, ingredients_alias, user_food_ids, food_ids_with_on_hand
            )

        ## Add filters and loader options
        if self.group_id:
            q = q.filter(self.model.group_id == self.group_id)
        if self.household_id:
            q = q.filter(self.model.household_id == self.household_id)
        if params.query_filter:
            try:
                query_filter_builder = QueryFilterBuilder(params.query_filter)
                q = query_filter_builder.filter_query(q, model=self.model)

            except ValueError as e:
                self.logger.error(e)
                raise HTTPException(status_code=400, detail=str(e)) from e

        q = self.add_order_by_to_query(q, params)
        q = q.limit(params.limit).options(*self._suggestion_loader_options(params, user_food_ids))

        ## Execute query
        try:
            data = self.session.execute(q).scalars().unique().all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        on_hand_food_ids = set(food_ids_with_on_hand)
        on_hand_tool_ids = set(tool_ids_with_on_hand)

        suggestions: list[RecipeSuggestionResponseItem] = []
        for result in data:
            recipe = cast(RecipeModel, result)

            # only check for missing foods and tools if the user has provided a list of them
            missing_foods, substituted_foods = (
                self._missing_and_substituted_foods(recipe, params, on_hand_food_ids) if user_food_ids else ([], [])
            )
            missing_tools = self._missing_tools(recipe, on_hand_tool_ids) if user_tool_ids else []

            suggestions.append(
                RecipeSuggestionResponseItem(
                    recipe=RecipeSummary.model_validate(recipe),
                    missing_foods=missing_foods,
                    substituted_foods=substituted_foods,
                    missing_tools=missing_tools,
                )
            )

        return suggestions
