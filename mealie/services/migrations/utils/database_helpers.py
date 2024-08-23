from __future__ import annotations

from collections.abc import Iterable
from typing import TYPE_CHECKING, TypeVar

from pydantic import BaseModel
from slugify import slugify
from sqlalchemy.orm import Session

from mealie.repos.all_repositories import AllRepositories
from mealie.schema.recipe import RecipeCategory
from mealie.schema.recipe.recipe import RecipeTag
from mealie.schema.recipe.recipe_category import CategoryOut, CategorySave, TagOut, TagSave

T = TypeVar("T", bound=BaseModel)

if TYPE_CHECKING:
    from mealie.repos.repository_generic import RepositoryGeneric


class DatabaseMigrationHelpers:
    def __init__(self, db: AllRepositories, session: Session) -> None:
        self.session = session
        self.db = db

    def _get_or_set_generic(
        self, accessor: RepositoryGeneric, items: Iterable[str], create_model: type[T], out_model: type[T]
    ) -> list[T]:
        """
        Utility model for getting or setting categories or tags. This will only work for those two cases.

        This is probably a bad implementation of this pattern.
        """
        items_out = []

        for item_name in items:
            slug_lookup = slugify(item_name)

            item_model = accessor.get_one(value=slug_lookup, key="slug", override_schema=out_model)

            if not item_model:
                item_model = accessor.create(
                    create_model(
                        group_id=self.db.group_id,
                        name=item_name,
                        slug=slug_lookup,
                    )
                )

            items_out.append(item_model.model_dump())
        return items_out

    def get_or_set_category(self, categories: Iterable[str]) -> list[RecipeCategory]:
        return self._get_or_set_generic(
            self.db.categories,
            categories,
            CategorySave,
            CategoryOut,
        )

    def get_or_set_tags(self, tags: Iterable[str]) -> list[RecipeTag]:
        return self._get_or_set_generic(
            self.db.tags,
            tags,
            TagSave,
            TagOut,
        )
