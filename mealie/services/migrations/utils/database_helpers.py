from typing import TypeVar

from pydantic import UUID4, BaseModel
from slugify import slugify
from sqlalchemy.orm import Session

from mealie.db.data_access_layer.access_model_factory import AccessModel
from mealie.db.database import Database
from mealie.schema.recipe import RecipeCategory
from mealie.schema.recipe.recipe import RecipeTag

T = TypeVar("T", bound=BaseModel)


class DatabaseMigrationHelpers:
    def __init__(self, db: Database, session: Session, group_id: int, user_id: UUID4) -> None:
        self.group_id = group_id
        self.user_id = user_id
        self.session = session
        self.db = db

    def _get_or_set_generic(self, accessor: AccessModel, items: list[str], out_model: T) -> list[T]:
        """
        Utility model for getting or setting categories or tags. This will only work for those two cases.

        This is probably a bad implementation of this pattern.
        """
        items_out = []

        for item_name in items:
            slug_lookup = slugify(item_name)

            item_model = accessor.get_one(slug_lookup, "slug", override_schema=out_model)

            if not item_model:
                item_model = accessor.create(
                    out_model(
                        name=item_name,
                        slug=slug_lookup,
                    )
                )

            items_out.append(item_model.dict())

        return items_out

    def get_or_set_category(self, categories: list[str]) -> list[RecipeCategory]:
        return self._get_or_set_generic(self.db.categories, categories, RecipeCategory)

    def get_or_set_tags(self, tags: list[str]) -> list[RecipeTag]:
        return self._get_or_set_generic(self.db.tags, tags, RecipeTag)
