import re as re
from collections.abc import Sequence
from random import randint
from uuid import UUID

from pydantic import UUID4
from slugify import slugify
from sqlalchemy import and_, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.ingredient import RecipeIngredientModel
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeCategory, RecipePagination, RecipeSummary, RecipeTag, RecipeTool
from mealie.schema.recipe.recipe_category import CategoryBase, TagBase
from mealie.schema.response.pagination import PaginationQuery

from ..db.models._model_base import SqlAlchemyBase
from ..schema._mealie.mealie_model import extract_uuids
from .repository_generic import RepositoryGeneric


class RepositoryRecipes(RepositoryGeneric[Recipe, RecipeModel]):
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

    def by_group(self, group_id: UUID) -> "RepositoryRecipes":
        return super().by_group(group_id)

    def get_all_public(self, limit: int | None = None, order_by: str | None = None, start=0, override_schema=None):
        eff_schema = override_schema or self.schema

        if order_by:
            order_attr = getattr(self.model, str(order_by))
            stmt = (
                select(self.model)
                .join(RecipeSettings)
                .filter(RecipeSettings.public == True)  # noqa: E712
                .order_by(order_attr.desc())
                .offset(start)
                .limit(limit)
            )
            return [eff_schema.from_orm(x) for x in self.session.execute(stmt).scalars().all()]

        stmt = (
            select(self.model)
            .join(RecipeSettings)
            .filter(RecipeSettings.public == True)  # noqa: E712
            .offset(start)
            .limit(limit)
        )
        return [eff_schema.from_orm(x) for x in self.session.execute(stmt).scalars().all()]

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

    def summary(
        self, group_id, start=0, limit=99999, load_foods=False, order_by="created_at", order_descending=True
    ) -> Sequence[RecipeModel]:
        args = [
            joinedload(RecipeModel.recipe_category),
            joinedload(RecipeModel.tags),
            joinedload(RecipeModel.tools),
        ]

        if load_foods:
            args.append(joinedload(RecipeModel.recipe_ingredient).options(joinedload(RecipeIngredientModel.food)))

        try:
            if order_by:
                order_attr = getattr(RecipeModel, order_by)
            else:
                order_attr = RecipeModel.created_at

        except AttributeError:
            self.logger.info(f'Attempted to sort by unknown sort property "{order_by}"; ignoring')
            order_attr = RecipeModel.created_at

        if order_descending:
            order_attr = order_attr.desc()

        else:
            order_attr = order_attr.asc()

        stmt = (
            select(RecipeModel)
            .options(*args)
            .filter(RecipeModel.group_id == group_id)
            .order_by(order_attr)
            .offset(start)
            .limit(limit)
        )
        return self.session.execute(stmt).scalars().all()

    def _uuids_for_items(self, items: list[UUID | str] | None, model: type[SqlAlchemyBase]) -> list[UUID] | None:
        if not items:
            return None
        ids: list[UUID] = []
        slugs: list[str] = []

        for i in items:
            if isinstance(i, UUID):
                ids.append(i)
            else:
                slugs.append(i)
        additional_ids = self.session.execute(select(model.id).filter(model.slug.in_(slugs))).scalars().all()
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
        require_all_categories=True,
        require_all_tags=True,
        require_all_tools=True,
        require_all_foods=True,
        search: str | None = None,
    ) -> RecipePagination:
        # Copy this, because calling methods (e.g. tests) might rely on it not getting mutated
        pagination_result = pagination.copy()
        q = select(self.model)

        args = [
            joinedload(RecipeModel.recipe_category),
            joinedload(RecipeModel.tags),
            joinedload(RecipeModel.tools),
        ]

        q = q.options(*args)

        fltr = self._filter_builder()
        q = q.filter_by(**fltr)

        if cookbook:
            cb_filters = self._build_recipe_filter(
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
            filters = self._build_recipe_filter(
                categories=category_ids,
                tags=tag_ids,
                tools=tool_ids,
                foods=foods,
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

        try:
            data = self.session.execute(q).scalars().unique().all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        items = [RecipeSummary.from_orm(item) for item in data]
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
            select(RecipeModel)
            .join(RecipeModel.recipe_category)
            .filter(RecipeModel.recipe_category.any(Category.id.in_(ids)))
        )
        return [RecipeSummary.from_orm(x) for x in self.session.execute(stmt).unique().scalars().all()]

    def _build_recipe_filter(
        self,
        categories: list[UUID4] | None = None,
        tags: list[UUID4] | None = None,
        tools: list[UUID4] | None = None,
        foods: list[UUID4] | None = None,
        require_all_categories: bool = True,
        require_all_tags: bool = True,
        require_all_tools: bool = True,
        require_all_foods: bool = True,
    ) -> list:
        if self.group_id:
            fltr = [
                RecipeModel.group_id == self.group_id,
            ]
        else:
            fltr = []

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
        stmt = select(RecipeModel).filter(*fltr)
        return [self.schema.from_orm(x) for x in self.session.execute(stmt).scalars().all()]

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
            select(RecipeModel).filter(and_(*filters)).order_by(func.random()).limit(1)  # Postgres and SQLite specific
        )
        return [self.schema.from_orm(x) for x in self.session.execute(stmt).scalars().all()]

    def get_random(self, limit=1) -> list[Recipe]:
        stmt = (
            select(RecipeModel)
            .filter(RecipeModel.group_id == self.group_id)
            .order_by(func.random())  # Postgres and SQLite specific
            .limit(limit)
        )
        return [self.schema.from_orm(x) for x in self.session.execute(stmt).scalars().all()]

    def get_by_slug(self, group_id: UUID4, slug: str, limit=1) -> Recipe | None:
        stmt = select(RecipeModel).filter(RecipeModel.group_id == group_id, RecipeModel.slug == slug)
        dbrecipe = self.session.execute(stmt).scalars().one_or_none()
        if dbrecipe is None:
            return None
        return self.schema.from_orm(dbrecipe)

    def all_ids(self, group_id: UUID4) -> Sequence[UUID4]:
        stmt = select(RecipeModel.id).filter(RecipeModel.group_id == group_id)
        return self.session.execute(stmt).scalars().all()
