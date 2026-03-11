from __future__ import annotations

from pydantic import UUID4, ConfigDict
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.schema._mealie import MealieModel
from mealie.schema.response.pagination import PaginationBase


class TagGroupIn(MealieModel):
    name: str
    color: str | None = None
    position: int = 0


class TagGroupSave(TagGroupIn):
    group_id: UUID4


class TagGroupBase(TagGroupIn):
    id: UUID4
    group_id: UUID4 | None = None
    slug: str
    model_config = ConfigDict(from_attributes=True)


class TagGroupOut(TagGroupSave):
    id: UUID4
    slug: str
    model_config = ConfigDict(from_attributes=True)


class TagGroupSummary(TagGroupBase):
    """Tag group with its associated tags"""

    tags: list[RecipeTagOut] = []
    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        from sqlalchemy.orm import selectinload

        from mealie.db.models.recipe.tag_group import TagGroup

        return [selectinload(TagGroup.tags)]


class TagGroupPagination(PaginationBase):
    items: list[TagGroupOut]


# deferred import to avoid circular dependency
from mealie.schema.recipe.recipe_category import TagOut as RecipeTagOut  # noqa: E402

TagGroupSummary.model_rebuild()
