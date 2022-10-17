from typing import Optional

from fastapi import BackgroundTasks, Depends
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.db.db_setup import generate_session
from mealie.services.event_bus_service.event_bus_listeners import (
    AppriseEventListener,
    EventListenerBase,
    WebhookEventListener,
)

from .event_types import Event, EventBusMessage, EventDocumentDataBase, EventTypes

settings = get_app_settings()
ALGORITHM = "HS256"


class EventSource:
    event_type: str
    item_type: str
    item_id: UUID4 | int
    kwargs: dict

    def __init__(self, event_type: str, item_type: str, item_id: UUID4 | int, **kwargs) -> None:
        self.event_type = event_type
        self.item_type = item_type
        self.item_id = item_id
        self.kwargs = kwargs

    def dict(self) -> dict:
        return {
            "event_type": self.event_type,
            "item_type": self.item_type,
            "item_id": str(self.item_id),
            **self.kwargs,
        }


class EventBusService:
    bg: BackgroundTasks | None
    session: Session | None
    group_id: UUID4 | None

    def __init__(
        self, bg: Optional[BackgroundTasks] = None, session: Optional[Session] = None, group_id: UUID4 | None = None
    ) -> None:
        self.bg = bg
        self.session = session
        self.group_id = group_id

        self.listeners: list[EventListenerBase] = [
            AppriseEventListener(self.session, self.group_id),
            WebhookEventListener(self.session, self.group_id),
        ]

    def dispatch(
        self,
        integration_id: str,
        group_id: UUID4,
        event_type: EventTypes,
        document_data: Optional[EventDocumentDataBase],
        message: str = "",
    ) -> None:
        self.group_id = group_id

        event = Event(
            message=EventBusMessage.from_type(event_type, body=message),
            event_type=event_type,
            integration_id=integration_id,
            document_data=document_data,
        )

        if self.bg:
            self.bg.add_task(self.publish_event, event=event)

        else:
            self.publish_event(event)

    def publish_event(self, event: Event) -> None:
        """Publishes the event to all listeners"""
        for listener in self.listeners:
            if subscribers := listener.get_subscribers(event):
                listener.publish_to_subscribers(event, subscribers)

    @classmethod
    def create(cls, bg: BackgroundTasks, session=Depends(generate_session), group_id: UUID4 | None = None):
        return cls(bg, session, group_id)
