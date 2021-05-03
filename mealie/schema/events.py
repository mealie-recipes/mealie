from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi_camelcase import CamelModel
from pydantic import Field


class EventCategory(str, Enum):
    general = "general"
    recipe = "recipe"
    backup = "backup"
    scheduled = "scheduled"
    migration = "migration"
    sign_up = "signup"


class Event(CamelModel):
    id: Optional[int]
    title: str
    text: str
    time_stamp: datetime = Field(default_factory=datetime.now)
    category: EventCategory = EventCategory.general

    class Config:
        orm_mode = True


class EventsOut(CamelModel):
    total: int
    events: list[Event]
