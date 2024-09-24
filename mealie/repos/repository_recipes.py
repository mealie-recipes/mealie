import re as re
from collections.abc import Sequence
from random import randint
from uuid import UUID

import sqlalchemy as sa
from pydantic import UUID4
from slugify import slugify
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import InstrumentedAttribute
from typing_extensions import Self

from mealie.db.models.household.household import Household
from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.ingredient import RecipeIngredientModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.db.models.users.user_to_recipe import UserToRecipe
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import (
    RecipeCategory,
    RecipePagination,
    RecipeSummary,
    RecipeTag,
    RecipeTool,
)
from mealie.schema.recipe.recipe_category import CategoryBase, TagBase
from mealie.schema.response.pagination import (
    OrderByNullPosition,
    OrderDirection,
    PaginationQuery,
)

from ..db.models._model_base import SqlAlchemyBase
from ..schema._mealie.mealie_model import extract_uuids
from .repository_generic import HouseholdRepositoryGeneric


class RepositoryRecipes(HouseholdRepositoryGeneric[Recipe, RecipeModel]):
    user_id: UUID4 | None = None

    def by_user(self: Self, user_id: UUID4) -> Self:
        """Add a user_id to the repo, which will be used to handle recipe ratings"""
        self.user_id = user_id
        return self

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
        additional_ids = self.session.execute(sa.select(model.id).filter(model.slug.in_(slugs))).scalars().all()
        return ids + additional_ids

    def add_order_attr_to_query(
        self,
        query: sa.Select,
        order_attr: InstrumentedAttribute,
        order_dir: OrderDirection,
        order_by_null: OrderByNullPosition | None,
    ) -> sa.Select:
        """Special handling for ordering recipes by rating"""
        column_name = order_attr.key
        if column_name != "rating" or not self.user_id:
            return super().add_order_attr_to_query(query, order_attr, order_dir, order_by_null)

        # calculate the effictive rating for the user by using the user's rating if it exists,
        # falling back to the recipe's rating if it doesn't
        effective_rating_column_name = "_effective_rating"
        query = query.add_columns(
            sa.case(
                (
                    sa.exists().where(
                        UserToRecipe.recipe_id == self.model.id,
                        UserToRecipe.user_id == self.user_id,
                        UserToRecipe.rating is not None,
                        UserToRecipe.rating > 0,
                    ),
                    sa.select(sa.func.max(UserToRecipe.rating))
                    .where(UserToRecipe.recipe_id == self.model.id, UserToRecipe.user_id == self.user_id)
                    .scalar_subquery(),
                ),
                else_=sa.case((self.model.rating == 0, None), else_=self.model.rating),
            ).label(effective_rating_column_name)
        )

        order_attr = effective_rating_column_name
        if order_dir is OrderDirection.asc:
            order_attr = sa.asc(order_attr)
        elif order_dir is OrderDirection.desc:
            order_attr = sa.desc(order_attr)

        if order_by_null is OrderByNullPosition.first:
            order_attr = sa.nulls_first(order_attr)
        else:
            order_attr = sa.nulls_last(order_attr)

        return query.order_by(order_attr)

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
            cb_filters = self._build_recipe_filter(
                households=[cookbook.household_id],
                categories=extract_uuids(cookbook.categories),
                tags=extract_uuids(cookbook.tags),
                tools=extract_uuids(cookbook.tools),
                require_all_categories=cookbook.require_all_categories,
                require_all_tags=cookbook.require_all_tags,
                require_all_tools=cookbook.require_all_tools,
            )

            q = q.filter(*cb_filters)
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

    def by_category_and_tags(
        self,
        categories: list[CategoryBase] | None = None,
        tags: list[TagBase] | None = None,
        tools: list[RecipeTool] | None = None,
        require_all_categories: bool = True,
        require_all_tags: bool = True,
        require_all_tools: bool = True,
    ) -> list[Recipe]:
        fltr = self._build_recipe_filter(
            categories=extract_uuids(categories) if categories else None,
            tags=extract_uuids(tags) if tags else None,
            tools=extract_uuids(tools) if tools else None,
            require_all_categories=require_all_categories,
            require_all_tags=require_all_tags,
            require_all_tools=require_all_tools,
        )
        stmt = sa.select(RecipeModel).filter(*fltr)
        return [self.schema.model_validate(x) for x in self.session.execute(stmt).scalars().all()]

    def get_random_by_categories_and_tags(
        self, categories: list[RecipeCategory], tags: list[RecipeTag]
    ) -> list[Recipe]:
        """
        get_random_by_categories returns a single random Recipe that contains every category provided
        in the list. This uses a function built in to Postgres and SQLite to get a random row limited
        to 1 entry.
        """

        # See Also:
        # - https://stackoverflow.com/questions/60805/getting-random-row-through-sqlalchemy

        filters = self._build_recipe_filter(extract_uuids(categories), extract_uuids(tags))  # type: ignore
        stmt = (
            sa.select(RecipeModel)
            .filter(sa.and_(*filters))
            .order_by(sa.func.random())
            .limit(1)  # Postgres and SQLite specific
        )
        return [self.schema.model_validate(x) for x in self.session.execute(stmt).scalars().all()]

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
