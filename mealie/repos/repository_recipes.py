from random import randint
from typing import Any

from sqlalchemy.orm import joinedload

from mealie.db.models.recipe.category import Category
from mealie.db.models.recipe.ingredient import RecipeIngredient
from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.schema.recipe import Recipe
from mealie.schema.recipe.recipe import RecipeCategory

from .repository_generic import RepositoryGeneric


class RepositoryRecipes(RepositoryGeneric[Recipe, RecipeModel]):
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
            .offset(start)
            .limit(limit)
            .all()
        )

    def get_by_categories(self, categories: list[RecipeCategory]) -> list[Recipe]:
        """
        get_by_categories returns all the Recipes that contain every category provided in the list
        """

        ids = [x.id for x in categories]

        return [
            self.schema.from_orm(x)
            for x in self.session.query(RecipeModel)
            .join(RecipeModel.recipe_category)
            .filter(RecipeModel.recipe_category.any(Category.id.in_(ids)))
            .all()
        ]
