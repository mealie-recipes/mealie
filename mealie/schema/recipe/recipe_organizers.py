"""
Categories, tags and tools: the organizers a recipe can carry.

Each organizer has the same shapes:

- `XCreate`: the body for creating or renaming one
- `XSave`: `XCreate` plus the group, as the repository stores it
- `XOut`: a saved organizer, both on its own and inside a recipe
- `XDraft`: an organizer inside a `RecipeDraft`, which may lack its id and slug until the server
  resolves or creates it
"""

from typing import Any, ClassVar

from pydantic import UUID4, ConfigDict, field_validator
from slugify import slugify
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.interfaces import LoaderOption

from mealie.db.models.recipe import Tool
from mealie.schema._mealie import MealieModel
from mealie.schema._mealie.mealie_model import MealieOutModel
from mealie.schema.response.pagination import PaginationBase


def _household_slugs(households: Any) -> Any:
    if not households:
        return []

    try:
        return [household.slug for household in households]
    except AttributeError:
        return households


class OrganizerMerge(MealieModel):
    """Moves every recipe from one organizer to another, then deletes the first one."""

    from_id: UUID4
    to_id: UUID4


class OrganizerOut(MealieOutModel):
    id: UUID4
    group_id: UUID4
    name: str
    slug: str
    recipe_count: int = 0
    """Only set where the query counts recipes, such as the organizer list routes."""

    _searchable_properties: ClassVar[list[str]] = ["name"]
    model_config = ConfigDict(from_attributes=True)


class OrganizerDraft(MealieModel):
    id: UUID4 | None = None
    group_id: UUID4 | None = None
    name: str
    slug: str | None = None
    recipe_count: int = 0

    _searchable_properties: ClassVar[list[str]] = ["name"]
    model_config = ConfigDict(from_attributes=True)

    def model_post_init(self, __context: Any) -> None:
        if not self.slug:
            self.slug = slugify(self.name)


# Categories


class CategoryCreate(MealieModel):
    name: str


class CategorySave(CategoryCreate):
    group_id: UUID4


class CategoryOut(OrganizerOut):
    pass


class CategoryDraft(OrganizerDraft):
    pass


class CategoryPagination(PaginationBase):
    items: list[CategoryOut]


# Tags


class TagCreate(MealieModel):
    name: str


class TagSave(TagCreate):
    group_id: UUID4


class TagOut(OrganizerOut):
    pass


class TagDraft(OrganizerDraft):
    pass


class TagPagination(PaginationBase):
    items: list[TagOut]


# Tools


class ToolCreate(MealieModel):
    name: str
    households_with_tool: list[str] = []


class ToolSave(ToolCreate):
    group_id: UUID4


class ToolOut(OrganizerOut):
    households_with_tool: list[str] = []
    """Slugs of the households that own this tool."""

    @field_validator("households_with_tool", mode="before")
    def convert_households_to_slugs(cls, v):
        return _household_slugs(v)

    @classmethod
    def loader_options(cls) -> list[LoaderOption]:
        return [selectinload(Tool.households_with_tool)]


class ToolDraft(OrganizerDraft):
    households_with_tool: list[str] = []

    @field_validator("households_with_tool", mode="before")
    def convert_households_to_slugs(cls, v):
        return _household_slugs(v)


class ToolPagination(PaginationBase):
    items: list[ToolOut]
