from typing import TypeVar

from pydantic import UUID4, BaseModel
from slugify import slugify
from sqlalchemy.orm import Session

from mealie.repos.all_repositories import AllRepositories
from mealie.repos.repository_factory import RepositoryGeneric
from mealie.schema.recipe import RecipeCategory
from mealie.schema.recipe.recipe import RecipeTag
from mealie.schema.recipe.recipe_category import CategoryOut, CategorySave, TagOut, TagSave

T = TypeVar("T", bound=BaseModel)


class DatabaseMigrationHelpers:
    def __init__(self, db: AllRepositories, session: Session, group_id: int, user_id: UUID4) -> None:
        self.group_id = group_id
        self.user_id = user_id
        self.session = session
        self.db = db

    def _get_or_set_generic(
        self, accessor: RepositoryGeneric, items: list[str], create_model: T, out_model: T
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
                        group_id=self.group_id,
                        name=item_name,
                        slug=slug_lookup,
                    )
                )

            items_out.append(item_model.dict())
        return items_out

    def get_or_set_category(self, categories: list[str]) -> list[RecipeCategory]:
        return self._get_or_set_generic(
            self.db.categories.by_group(self.group_id),
            categories,
            CategorySave,
            CategoryOut,
        )

    def get_or_set_tags(self, tags: list[str]) -> list[RecipeTag]:
        return self._get_or_set_generic(
            self.db.tags.by_group(self.group_id),
            tags,
            TagSave,
            TagOut,
        )
