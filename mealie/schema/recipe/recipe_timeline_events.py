from datetime import datetime
from enum import Enum
from pathlib import Path

from pydantic import UUID4, Field

from mealie.core.config import get_app_dirs
from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.recipe.recipe import Recipe
from mealie.schema.response.pagination import PaginationBase

app_dirs = get_app_dirs()


class TimelineEventType(Enum):
    system = "system"
    info = "info"
    comment = "comment"


class TimelineEventImage(Enum):
    has_image = "has image"
    does_not_have_image = "does not have image"


class RecipeTimelineEventIn(MealieModel):
    recipe_id: UUID4
    user_id: UUID4 | None = None
    """can be inferred in some contexts, so it's not required"""

    subject: str
    event_type: TimelineEventType

    message: str | None = Field(None, alias="eventMessage")
    image: TimelineEventImage | None = TimelineEventImage.does_not_have_image

    timestamp: datetime = datetime.now()

    class Config:
        use_enum_values = True


class RecipeTimelineEventCreate(RecipeTimelineEventIn):
    user_id: UUID4


class RecipeTimelineEventUpdate(MealieModel):
    subject: str
    message: str | None = Field(alias="eventMessage")
    image: TimelineEventImage | None = None

    class Config:
        use_enum_values = True


class RecipeTimelineEventOut(RecipeTimelineEventCreate):
    id: UUID4
    created_at: datetime
    update_at: datetime

    class Config:
        orm_mode = True

    @classmethod
    def image_dir_from_id(cls, recipe_id: UUID4 | str, timeline_event_id: UUID4 | str) -> Path:
        return Recipe.timeline_image_dir_from_id(recipe_id, timeline_event_id)

    @property
    def image_dir(self) -> Path:
        return self.image_dir_from_id(self.recipe_id, self.id)


class RecipeTimelineEventPagination(PaginationBase):
    items: list[RecipeTimelineEventOut]
