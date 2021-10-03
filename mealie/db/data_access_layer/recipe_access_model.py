from random import randint
from typing import Any

from sqlalchemy.orm import joinedload

from mealie.db.models.recipe.recipe import RecipeModel
from mealie.db.models.recipe.settings import RecipeSettings
from mealie.schema.recipe import Recipe

from ._access_model import AccessModel


class RecipeDataAccessModel(AccessModel[Recipe, RecipeModel]):
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

    def summary(self, group_id, start=0, limit=99999) -> Any:
        return (
            self.session.query(RecipeModel)
            .options(joinedload(RecipeModel.recipe_category), joinedload(RecipeModel.tags))
            .filter(RecipeModel.group_id == group_id)
            .offset(start)
            .limit(limit)
            .all()
        )
