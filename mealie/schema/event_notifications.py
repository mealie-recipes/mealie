from enum import Enum
from typing import Optional

from fastapi_camelcase import CamelModel


class DeclaredTypes(str, Enum):
    general = "General"
    discord = "Discord"
    gotify = "Gotify"
    pushover = "Pushover"
    home_assistant = "Home Assistant"


class EventNotificationOut(CamelModel):
    id: Optional[int]
    name: str = ""
    type: DeclaredTypes = DeclaredTypes.general
    general: bool = True
    recipe: bool = True
    backup: bool = True
    scheduled: bool = True
    migration: bool = True
    group: bool = True
    user: bool = True

    class Config:
        orm_mode = True


class EventNotificationIn(EventNotificationOut):
    notification_url: str = ""

    class Config:
        orm_mode = True


class Discord(CamelModel):
    webhook_id: str
    webhook_token: str

    @property
    def create_url(self) -> str:
        return f"discord://{self.webhook_id}/{self.webhook_token}/"


class GotifyPriority(str, Enum):
    low = "low"
    moderate = "moderate"
    normal = "normal"
    high = "high"


class Gotify(CamelModel):
    hostname: str
    token: str
    priority: GotifyPriority = GotifyPriority.normal

    @property
    def create_url(self) -> str:
        return f"gotifys://{self.hostname}/{self.token}/?priority={self.priority}"
