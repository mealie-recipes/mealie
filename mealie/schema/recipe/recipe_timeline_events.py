from datetime import datetime
from enum import Enum

from pydantic import UUID4, Field

from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.response.pagination import PaginationBase


class TimelineEventType(Enum):
    system = "system"
    info = "info"
    comment = "comment"


class RecipeTimelineEventIn(MealieModel):
    user_id: UUID4 | None = None
    """can be inferred in some contexts, so it's not required"""

    subject: str
    event_type: TimelineEventType

    message: str | None = Field(alias="eventMessage")
    image: str | None = None

    timestamp: datetime = datetime.now()

    class Config:
        use_enum_values = True


class RecipeTimelineEventCreate(RecipeTimelineEventIn):
    recipe_id: UUID4
    user_id: UUID4


class RecipeTimelineEventUpdate(MealieModel):
    subject: str
    message: str | None = Field(alias="eventMessage")
    image: str | None = None


class RecipeTimelineEventOut(RecipeTimelineEventCreate):
    id: UUID4
    created_at: datetime
    update_at: datetime

    class Config:
        orm_mode = True


class RecipeTimelineEventPagination(PaginationBase):
    items: list[RecipeTimelineEventOut]
