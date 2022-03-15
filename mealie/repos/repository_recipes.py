from random import randint
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import and_, func
from sqlalchemy.orm import joinedload

from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.ingredient import RecipeIngredient
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.db.models.recipe.tag import Tag
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeCategory, RecipeSummary, RecipeTag

from .repository_generic import RepositoryGeneric


class RepositoryRecipes(RepositoryGeneric[Recipe, RecipeModel]):
    def by_group(self, group_id: UUID) -> "RepositoryRecipes":
        return super().by_group(group_id)

    def get_all_public(self, limit: int = None, order_by: str = None, start=0, override_schema=None):
        eff_schema = override_schema or self.schema

        if order_by:
            order_attr = getattr(self.sql_model, str(order_by))

            return [
                eff_schema.from_orm(x)
                for x in self.session.query(self.sql_model)
                .join(RecipeSettings)
                .filter(RecipeSettings.public == True)  # noqa: 711
                .order_by(order_attr.desc())
                .offset(start)
                .limit(limit)
                .all()
            ]

        return [
            eff_schema.from_orm(x)
            for x in self.session.query(self.sql_model)
            .join(RecipeSettings)
            .filter(RecipeSettings.public == True)  # noqa: 711
            .offset(start)
            .limit(limit)
            .all()
        ]

    def update_image(self, slug: str, _: str = None) -> str:
        entry: RecipeModel = self._query_one(match_value=slug)
        entry.image = randint(0, 255)
        self.session.commit()

        return entry.image

    def count_uncategorized(self, count=True, override_schema=None) -> int:
        return self._count_attribute(
            attribute_name=RecipeModel.recipe_category,
            attr_match=None,
            count=count,
            override_schema=override_schema,
        )

    def count_untagged(self, count=True, override_schema=None) -> int:
        return self._count_attribute(
            attribute_name=RecipeModel.tags,
            attr_match=None,
            count=count,
            override_schema=override_schema,
        )

    def summary(self, group_id, start=0, limit=99999, load_foods=False) -> Any:
        args = [
            joinedload(RecipeModel.recipe_category),
            joinedload(RecipeModel.tags),
            joinedload(RecipeModel.tools),
        ]

        if load_foods:
            args.append(joinedload(RecipeModel.recipe_ingredient).options(joinedload(RecipeIngredient.food)))

        return (
            self.session.query(RecipeModel)
            .options(*args)
            .filter(RecipeModel.group_id == group_id)
            .order_by(RecipeModel.date_added.desc())
            .offset(start)
            .limit(limit)
            .all()
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

    def get_random_by_categories_and_tags(self, categories: list[RecipeCategory], tags: list[RecipeTag]) -> Recipe:
        """
        get_random_by_categories returns a single random Recipe that contains every category provided
        in the list. This uses a function built in to Postgres and SQLite to get a random row limited
        to 1 entry.
        """

        # See Also:
        # - https://stackoverflow.com/questions/60805/getting-random-row-through-sqlalchemy

        filters = [
            RecipeModel.group_id == self.group_id,
        ]

        if categories:
            cat_ids = [x.id for x in categories]
            filters.extend(RecipeModel.recipe_category.any(Category.id.is_(cat_id)) for cat_id in cat_ids)

        if tags:
            tag_ids = [x.id for x in tags]
            filters.extend(RecipeModel.tags.any(Tag.id.is_(tag_id)) for tag_id in tag_ids)

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

    def get_by_slug(self, group_id: UUID, slug: str, limit=1) -> Optional[Recipe]:
        dbrecipe = (
            self.session.query(RecipeModel)
            .filter(RecipeModel.group_id == group_id, RecipeModel.slug == slug)
            .one_or_none()
        )
        if dbrecipe is None:
            return None
        return self.schema.from_orm(dbrecipe)
