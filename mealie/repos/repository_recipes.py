from random import randint
from typing import Any, Optional
from uuid import UUID

from pydantic import UUID4
from slugify import slugify
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.ingredient import RecipeIngredient
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.recipe.tag import Tag
from mealie.db.models.recipe.tool import Tool
from mealie.schema.cookbook.cookbook import ReadCookBook
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeCategory, RecipePagination, RecipeSummary, RecipeTag, RecipeTool
from mealie.schema.recipe.recipe_category import CategoryBase, TagBase
from mealie.schema.response.pagination import PaginationQuery

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
        return super().by_group(group_id)  # type: ignore

    def get_all_public(self, limit: int = None, order_by: str = None, start=0, override_schema=None):
        eff_schema = override_schema or self.schema

        if order_by:
            order_attr = getattr(self.model, str(order_by))

            return [
                eff_schema.from_orm(x)
                for x in self.session.query(self.model)
                .join(RecipeSettings)
                .filter(RecipeSettings.public == True)  # noqa: 711
                .order_by(order_attr.desc())
                .offset(start)
                .limit(limit)
                .all()
            ]

        return [
            eff_schema.from_orm(x)
            for x in self.session.query(self.model)
            .join(RecipeSettings)
            .filter(RecipeSettings.public == True)  # noqa: 711
            .offset(start)
            .limit(limit)
            .all()
        ]

    def update_image(self, slug: str, _: str = None) -> int:
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
    ) -> Any:
        args = [
            joinedload(RecipeModel.recipe_category),
            joinedload(RecipeModel.tags),
            joinedload(RecipeModel.tools),
        ]

        if load_foods:
            args.append(joinedload(RecipeModel.recipe_ingredient).options(joinedload(RecipeIngredient.food)))

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

        return (
            self.session.query(RecipeModel)
            .options(*args)
            .filter(RecipeModel.group_id == group_id)
            .order_by(order_attr)
            .offset(start)
            .limit(limit)
            .all()
        )

    def page_all(
        self,
        pagination: PaginationQuery,
        override=None,
        load_food=False,
        cookbook: Optional[ReadCookBook] = None,
        categories: Optional[list[UUID4 | str]] = None,
        tags: Optional[list[UUID4 | str]] = None,
        tools: Optional[list[UUID4 | str]] = None,
    ) -> RecipePagination:
        q = self.session.query(self.model)

        args = [
            joinedload(RecipeModel.recipe_category),
            joinedload(RecipeModel.tags),
            joinedload(RecipeModel.tools),
        ]

        if load_food:
            args.append(joinedload(RecipeModel.recipe_ingredient).options(joinedload(RecipeIngredient.food)))

        q = q.options(*args)

        fltr = self._filter_builder()
        q = q.filter_by(**fltr)

        if cookbook:
            cb_filters = self._category_tag_filters(
                cookbook.categories,
                cookbook.tags,
                cookbook.tools,
                cookbook.require_all_categories,
                cookbook.require_all_tags,
                cookbook.require_all_tools,
            )

            q = q.filter(*cb_filters)

        if categories:
            for category in categories:
                if isinstance(category, UUID):
                    q = q.filter(RecipeModel.recipe_category.any(Category.id == category))

                else:
                    q = q.filter(RecipeModel.recipe_category.any(Category.slug == category))

        if tags:
            for tag in tags:
                if isinstance(tag, UUID):
                    q = q.filter(RecipeModel.tags.any(Tag.id == tag))

                else:
                    q = q.filter(RecipeModel.tags.any(Tag.slug == tag))

        if tools:
            for tool in tools:
                if isinstance(tool, UUID):
                    q = q.filter(RecipeModel.tools.any(Tool.id == tool))

                else:
                    q = q.filter(RecipeModel.tools.any(Tool.slug == tool))

        q, count, total_pages = self.add_pagination_to_query(q, pagination)

        try:
            data = q.all()
        except Exception as e:
            self._log_exception(e)
            self.session.rollback()
            raise e

        return RecipePagination(
            page=pagination.page,
            per_page=pagination.per_page,
            total=count,
            total_pages=total_pages,
            items=data,
        )

    def get_by_categories(self, categories: list[RecipeCategory]) -> list[RecipeSummary]:
        """
        get_by_categories returns all the Recipes that contain every category provided in the list
        """

        ids = [x.id for x in categories]

        return [
            RecipeSummary.from_orm(x)
            for x in self.session.query(RecipeModel)
            .join(RecipeModel.recipe_category)
            .filter(RecipeModel.recipe_category.any(Category.id.in_(ids)))
            .all()
        ]

    def _category_tag_filters(
        self,
        categories: list[CategoryBase] | None = None,
        tags: list[TagBase] | None = None,
        tools: list[RecipeTool] | None = None,
        require_all_categories: bool = True,
        require_all_tags: bool = True,
        require_all_tools: bool = True,
    ) -> list:
        fltr = [
            RecipeModel.group_id == self.group_id,
        ]

        if categories:
            cat_ids = [x.id for x in categories]
            if require_all_categories:
                fltr.extend(RecipeModel.recipe_category.any(Category.id == cat_id) for cat_id in cat_ids)
            else:
                fltr.append(RecipeModel.recipe_category.any(Category.id.in_(cat_ids)))

        if tags:
            tag_ids = [x.id for x in tags]
            if require_all_tags:
                fltr.extend(RecipeModel.tags.any(Tag.id.is_(tag_id)) for tag_id in tag_ids)
            else:
                fltr.append(RecipeModel.tags.any(Tag.id.in_(tag_ids)))

        if tools:
            tool_ids = [x.id for x in tools]

            if require_all_tools:
                fltr.extend(RecipeModel.tools.any(Tool.id == tool_id) for tool_id in tool_ids)
            else:
                fltr.append(RecipeModel.tools.any(Tool.id.in_(tool_ids)))

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
        fltr = self._category_tag_filters(
            categories, tags, tools, require_all_categories, require_all_tags, require_all_tools
        )

        return [self.schema.from_orm(x) for x in self.session.query(RecipeModel).filter(*fltr).all()]

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

        filters = self._category_tag_filters(categories, tags)  # type: ignore

        return [
            self.schema.from_orm(x)
            for x in self.session.query(RecipeModel)
            .filter(and_(*filters))
            .order_by(func.random())  # Postgres and SQLite specific
            .limit(1)
        ]

    def get_random(self, limit=1) -> list[Recipe]:
        return [
            self.schema.from_orm(x)
            for x in self.session.query(RecipeModel)
            .filter(RecipeModel.group_id == self.group_id)
            .order_by(func.random())  # Postgres and SQLite specific
            .limit(limit)
        ]

    def get_by_slug(self, group_id: UUID4, slug: str, limit=1) -> Optional[Recipe]:
        dbrecipe = (
            self.session.query(RecipeModel)
            .filter(RecipeModel.group_id == group_id, RecipeModel.slug == slug)
            .one_or_none()
        )
        if dbrecipe is None:
            return None
        return self.schema.from_orm(dbrecipe)

    def all_ids(self, group_id: UUID4) -> list[UUID4]:
        return [tpl[0] for tpl in self.session.query(RecipeModel.id).filter(RecipeModel.group_id == group_id).all()]
