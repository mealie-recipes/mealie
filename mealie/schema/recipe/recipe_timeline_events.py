from datetime import datetime

from pydantic import UUID4

from mealie.db.models.recipe.recipe_timeline import TimelineEventType
from mealie.schema._mealie.mealie_model import MealieModel
from mealie.schema.response.pagination import PaginationBase


class RecipeTimelineEventIn(MealieModel):
    # can be inferred in some contexts, so it's not required
    user_id: UUID4 | None = None

    subject: str
    event_type: TimelineEventType

    message: str | None = None
    image: str | None = None

    event_dt: datetime = datetime.now()


class RecipeTimelineEventCreate(RecipeTimelineEventIn):
    recipe_id: UUID4
    user_id: UUID4


class RecipeTimelineEventUpdate(MealieModel):
    subject: str
    message: str | None = None
    image: str | None = None


class RecipeTimelineEventOut(RecipeTimelineEventCreate):
    id: UUID4
    created_at: datetime
    update_at: datetime

    class Config:
        orm_mode = True


class RecipeTimelineEventPagination(PaginationBase):
    items: list[RecipeTimelineEventOut]
