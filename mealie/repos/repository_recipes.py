import re as re
from collections.abc import Sequence
from random import randint
from typing import Self, cast
from uuid import UUID

import sqlalchemy as sa
from fastapi import HTTPException
from pydantic import UUID4
from slugify import slugify
from sqlalchemy import orm
from sqlalchemy.exc import IntegrityError

from mealie.db.models.household import Household, HouseholdToRecipe
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.ingredient import RecipeIngredientModel, households_to_ingredient_foods
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool, households_to_tools, recipes_to_tools
from mealie.db.models.users.user_to_recipe import UserToRecipe
from mealie.db.models.users.users import User
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeCategory, RecipePagination, RecipeSummary
from mealie.schema.recipe.recipe_ingredient import IngredientFood
from mealie.schema.recipe.recipe_suggestion import RecipeSuggestionQuery, RecipeSuggestionResponseItem
from mealie.schema.recipe.recipe_tool import RecipeToolOut
from mealie.schema.response.pagination import PaginationQuery
from mealie.schema.response.query_filter import QueryFilterBuilder

from ..db.models._model_base import SqlAlchemyBase
from .repository_generic import HouseholdRepositoryGeneric


class RepositoryRecipes(HouseholdRepositoryGeneric[Recipe, RecipeModel]):
    user_id: UUID4 | None = None

    @property
    def column_aliases(self):
        if not self.user_id:
            return {}

        return {
            "last_made": self._get_last_made_col_alias(),
            "rating": self._get_rating_col_alias(),
        }

    def by_user(self: Self, user_id: UUID4) -> Self:
        """Add a user_id to the repo, which will be used to handle recipe ratings and other user-specific data"""
        self.user_id = user_id
        return self

    def _get_last_made_col_alias(self) -> sa.ColumnElement | None:
        """Computed last_made which uses `HouseholdToRecipe.last_made` for the user's household, otherwise None"""

        user_household_subquery = sa.select(User.household_id).where(User.id == self.user_id).scalar_subquery()
        return (
            sa.select(HouseholdToRecipe.last_made)
            .where(
                HouseholdToRecipe.recipe_id == self.model.id,
                HouseholdToRecipe.household_id == user_household_subquery,
            )
            .correlate(self.model)
            .scalar_subquery()
        )

    def _get_rating_col_alias(self) -> sa.ColumnElement | None:
        """Computed rating which uses the user's rating if it exists, otherwise falling back to the recipe's rating"""

        effective_rating = sa.case(
            (
                sa.exists().where(
                    UserToRecipe.recipe_id == self.model.id,
                    UserToRecipe.user_id == self.user_id,
                    UserToRecipe.rating != None,  # noqa E711
                    UserToRecipe.rating > 0,
                ),
                sa.select(sa.func.max(UserToRecipe.rating))
                .where(UserToRecipe.recipe_id == self.model.id, UserToRecipe.user_id == self.user_id)
                .correlate(self.model)
                .scalar_subquery(),
            ),
            else_=sa.case(
                (self.model.rating == 0, None),
                else_=self.model.rating,
            ),
        )
        return sa.cast(effective_rating, sa.Float)

    def create(self, document: Recipe) -> Recipe:  # type: ignore
        max_retries = 10
        original_name: str = document.name  # type: ignore

        for i in range(1, 11):
            try:
                return super().create(document)
            except IntegrityError:
                self.session.rollback()
                document.name = f"{original_name} ({i})"
                document.slug = slugify(document.name)

                if i >= max_retries:
                    raise

    def update_image(self, slug: str, _: str | None = None) -> int:
        entry: RecipeModel = self._query_one(match_value=slug)
        entry.image = randint(0, 255)
        self.session.commit()

        return entry.image

    def count_uncategorized(self, count=True, override_schema=None):
        return self._count_attribute(
            attribute_name=RecipeModel.recipe_category,
            attr_match=None,
            count=count,
            override_schema=override_schema,
        )

    def count_untagged(self, count=True, override_schema=None):
        return self._count_attribute(
            attribute_name=RecipeModel.tags,
            attr_match=None,
            count=count,
            override_schema=override_schema,
        )

    def _uuids_for_items(self, items: list[UUID | str] | None, model: type[SqlAlchemyBase]) -> list[UUID] | None:
        if not items:
            return None
        ids: list[UUID] = []
        slugs: list[str] = []

        for i in items:
            if isinstance(i, UUID):
                ids.append(i)
            else:
                try:
                    i_as_uuid = UUID(i)
                    ids.append(i_as_uuid)
                except ValueError:
                    slugs.append(i)

        if not slugs:
            return ids
        additional_ids = self.session.execute(sa.select(model.id).filter(model.slug.in_(slugs))).scalars().all()
        return ids + additional_ids

    def page_all(  # type: ignore
        self,
        pagination: PaginationQuery,
        override=None,
        cookbook: ReadCookBook | None = None,
        categories: list[UUID4 | str] | None = None,
        tags: list[UUID4 | str] | None = None,
        tools: list[UUID4 | str] | None = None,
        foods: list[UUID4 | str] | None = None,
        households: list[UUID4 | str] | None = None,
        require_all_categories=True,
        require_all_tags=True,
        require_all_tools=True,
        require_all_foods=True,
        search: str | None = None,
    ) -> RecipePagination:
        # Copy this, because calling methods (e.g. tests) might rely on it not getting mutated
        pagination_result = pagination.model_copy()
        q = sa.select(self.model)

        fltr = self._filter_builder()
        q = q.filter_by(**fltr)

        if cookbook:
            if pagination_result.query_filter and cookbook.query_filter_string:
                pagination_result.query_filter = (
                    f"({pagination_result.query_filter}) AND ({cookbook.query_filter_string})"
                )
            else:
                pagination_result.query_filter = cookbook.query_filter_string
        else:
            category_ids = self._uuids_for_items(categories, Category)
            tag_ids = self._uuids_for_items(tags, Tag)
            tool_ids = self._uuids_for_items(tools, Tool)
            household_ids = self._uuids_for_items(households, Household)
            filters = self._build_recipe_filter(
                categories=category_ids,
                tags=tag_ids,
                tools=tool_ids,
                foods=foods,
                households=household_ids,
                require_all_categories=require_all_categories,
                require_all_tags=require_all_tags,
                require_all_tools=require_all_tools,
                require_all_foods=require_all_foods,
            )
            q = q.filter(*filters)
        if search:
            q = self.add_search_to_query(q, self.schema, search)

        if not pagination_result.order_by and not search:
            # default ordering if not searching
            pagination_result.order_by = "created_at"

        q, count, total_pages = self.add_pagination_to_query(q, pagination_result)

        # Apply options late, so they do not get used for counting
        q = q.options(*RecipeSummary.loader_options())
        try:
            data = self.session.execute(q).scalars().unique().all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        items = [RecipeSummary.model_validate(item) for item in data]
        return RecipePagination(
            page=pagination_result.page,
            per_page=pagination_result.per_page,
            total=count,
            total_pages=total_pages,
            items=items,
        )

    def get_by_categories(self, categories: list[RecipeCategory]) -> list[RecipeSummary]:
        """
        get_by_categories returns all the Recipes that contain every category provided in the list
        """

        ids = [x.id for x in categories]
        stmt = (
            sa.select(RecipeModel)
            .join(RecipeModel.recipe_category)
            .filter(RecipeModel.recipe_category.any(Category.id.in_(ids)))
        )
        if self.group_id:
            stmt = stmt.filter(RecipeModel.group_id == self.group_id)
        if self.household_id:
            stmt = stmt.filter(RecipeModel.household_id == self.household_id)

        return [RecipeSummary.model_validate(x) for x in self.session.execute(stmt).unique().scalars().all()]

    def _build_recipe_filter(
        self,
        categories: list[UUID4] | None = None,
        tags: list[UUID4] | None = None,
        tools: list[UUID4] | None = None,
        foods: list[UUID4] | None = None,
        households: list[UUID4] | None = None,
        require_all_categories: bool = True,
        require_all_tags: bool = True,
        require_all_tools: bool = True,
        require_all_foods: bool = True,
    ) -> list:
        fltr: list[sa.ColumnElement] = []
        if self.group_id:
            fltr.append(RecipeModel.group_id == self.group_id)
        if self.household_id:
            fltr.append(RecipeModel.household_id == self.household_id)

        if categories:
            if require_all_categories:
                fltr.extend(RecipeModel.recipe_category.any(Category.id == cat_id) for cat_id in categories)
            else:
                fltr.append(RecipeModel.recipe_category.any(Category.id.in_(categories)))

        if tags:
            if require_all_tags:
                fltr.extend(RecipeModel.tags.any(Tag.id == tag_id) for tag_id in tags)
            else:
                fltr.append(RecipeModel.tags.any(Tag.id.in_(tags)))

        if tools:
            if require_all_tools:
                fltr.extend(RecipeModel.tools.any(Tool.id == tool_id) for tool_id in tools)
            else:
                fltr.append(RecipeModel.tools.any(Tool.id.in_(tools)))
        if foods:
            if require_all_foods:
                fltr.extend(RecipeModel.recipe_ingredient.any(RecipeIngredientModel.food_id == food) for food in foods)
            else:
                fltr.append(RecipeModel.recipe_ingredient.any(RecipeIngredientModel.food_id.in_(foods)))
        if households:
            fltr.append(RecipeModel.household_id.in_(households))
        return fltr

    def get_random(self, limit=1) -> list[Recipe]:
        stmt = sa.select(RecipeModel).order_by(sa.func.random()).limit(limit)  # Postgres and SQLite specific
        if self.group_id:
            stmt = stmt.filter(RecipeModel.group_id == self.group_id)
        if self.household_id:
            stmt = stmt.filter(RecipeModel.household_id == self.household_id)

        return [self.schema.model_validate(x) for x in self.session.execute(stmt).scalars().all()]

    def get_by_slug(self, group_id: UUID4, slug: str) -> Recipe | None:
        stmt = sa.select(RecipeModel).filter(RecipeModel.group_id == group_id, RecipeModel.slug == slug)
        dbrecipe = self.session.execute(stmt).scalars().one_or_none()
        if dbrecipe is None:
            return None
        return self.schema.model_validate(dbrecipe)

    def all_ids(self, group_id: UUID4) -> Sequence[UUID4]:
        stmt = sa.select(RecipeModel.id).filter(RecipeModel.group_id == group_id)
        return self.session.execute(stmt).scalars().all()

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

        # preserve the original lists of ids before we add on_hand items
        food_ids_with_on_hand = user_food_ids.copy()
        tool_ids_with_on_hand = user_tool_ids.copy()

        if params.include_foods_on_hand and self.user_id:
            foods_on_hand_query = (
                sa.select(households_to_ingredient_foods.c.food_id)
                .join(User, households_to_ingredient_foods.c.household_id == User.household_id)
                .filter(
                    sa.not_(households_to_ingredient_foods.c.food_id.in_(food_ids_with_on_hand)),
                    User.id == self.user_id,
                )
            )
            foods_on_hand = self.session.execute(foods_on_hand_query).scalars().all()
            food_ids_with_on_hand.extend(foods_on_hand)

        if params.include_tools_on_hand and self.user_id:
            tools_on_hand_query = (
                sa.select(households_to_tools.c.tool_id)
                .join(User, households_to_tools.c.household_id == User.household_id)
                .filter(
                    sa.not_(households_to_tools.c.tool_id.in_(tool_ids_with_on_hand)),
                    User.id == self.user_id,
                )
            )
            tools_on_hand = self.session.execute(tools_on_hand_query).scalars().all()
            tool_ids_with_on_hand.extend(tools_on_hand)

        ## Build suggestion query
        settings_alias = orm.aliased(RecipeSettings)
        ingredients_alias = orm.aliased(RecipeIngredientModel)
        tools_alias = orm.aliased(Tool)

        q = sa.select(self.model)
        fltr = self._filter_builder()
        q = q.filter_by(**fltr)

        # Tools goes first so we can order by missing tools count before foods
        if user_tool_ids:
            unmatched_tools_query = (
                sa.select(recipes_to_tools.c.recipe_id, sa.func.count().label("unmatched_tools_count"))
                .join(tools_alias, recipes_to_tools.c.tool_id == tools_alias.id)
                .filter(sa.not_(tools_alias.id.in_(tool_ids_with_on_hand)))
                .group_by(recipes_to_tools.c.recipe_id)
                .subquery()
            )
            q = (
                q.outerjoin(unmatched_tools_query, self.model.id == unmatched_tools_query.c.recipe_id)
                .filter(
                    sa.or_(
                        unmatched_tools_query.c.unmatched_tools_count.is_(None),
                        unmatched_tools_query.c.unmatched_tools_count <= params.max_missing_tools,
                    )
                )
                .order_by(unmatched_tools_query.c.unmatched_tools_count.asc().nulls_first())
            )

        if user_food_ids:
            unmatched_foods_query = (
                sa.select(ingredients_alias.recipe_id, sa.func.count().label("unmatched_foods_count"))
                .filter(sa.not_(ingredients_alias.food_id.in_(food_ids_with_on_hand)))
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
            q = (
                q.join(settings_alias, self.model.settings)
                .filter(settings_alias.disable_amount == False)  # noqa: E712 - required for SQLAlchemy comparison
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

            # only include recipes that have at least one food in the user's list
            if user_food_ids:
                q = q.filter(total_user_foods_query.c.total_user_foods_count > 0)

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
        q = q.limit(params.limit).options(*RecipeSummary.loader_options())

        ## Execute query
        try:
            data = self.session.execute(q).scalars().unique().all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        suggestions: list[RecipeSuggestionResponseItem] = []
        for result in data:
            recipe = cast(RecipeModel, result)

            missing_foods: list[IngredientFood] = []
            if user_food_ids:  # only check for missing foods if the user has provided a list of foods
                seen_food_ids: set[UUID4] = set()
                seen_food_ids.update(food_ids_with_on_hand)
                for ingredient in recipe.recipe_ingredient:
                    if not ingredient.food:
                        continue
                    if ingredient.food.id in seen_food_ids:
                        continue

                    seen_food_ids.add(ingredient.food.id)
                    missing_foods.append(IngredientFood.model_validate(ingredient.food))

            missing_tools: list[RecipeToolOut] = []
            if user_tool_ids:  # only check for missing tools if the user has provided a list of tools
                seen_tool_ids: set[UUID4] = set()
                seen_tool_ids.update(tool_ids_with_on_hand)
                for tool in recipe.tools:
                    if tool.id in seen_tool_ids:
                        continue

                    seen_tool_ids.add(tool.id)
                    missing_tools.append(RecipeToolOut.model_validate(tool))

            suggestion = RecipeSuggestionResponseItem(
                recipe=RecipeSummary.model_validate(recipe),
                missing_foods=missing_foods,
                missing_tools=missing_tools,
            )
            suggestions.append(suggestion)

        return suggestions
