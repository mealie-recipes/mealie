from fastapi import BackgroundTasks, Depends
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.core.config import get_app_settings
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.response.pagination import PaginationQuery
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
    bg: BackgroundTasks | None = None
    session: Session | None = None

    def __init__(
        self,
        bg: BackgroundTasks | None = None,
        session: Session | None = None,
    ) -> None:
        self.bg = bg
        self.session = session

    def _get_listeners(self, group_id: UUID4, household_id: UUID4) -> list[EventListenerBase]:
        return [
            AppriseEventListener(group_id, household_id),
            WebhookEventListener(group_id, household_id),
        ]

    def _publish_event(self, event: Event, group_id: UUID4, household_id: UUID4) -> None:
        """Publishes the event to all listeners"""
        for listener in self._get_listeners(group_id, household_id):
            if subscribers := listener.get_subscribers(event):
                listener.publish_to_subscribers(event, subscribers)

    def dispatch(
        self,
        integration_id: str,
        group_id: UUID4,
        household_id: UUID4 | None,
        event_type: EventTypes,
        document_data: EventDocumentDataBase | None,
        message: str = "",
    ) -> None:
        event = Event(
            message=EventBusMessage.from_type(event_type, body=message),
            event_type=event_type,
            integration_id=integration_id,
            document_data=document_data,
        )

        if not household_id:
            if not self.session:
                raise ValueError("Session is required if household_id is not provided")

            repos = get_repositories(self.session, group_id=group_id)
            households = repos.households.page_all(PaginationQuery(page=1, per_page=-1)).items
            household_ids = [household.id for household in households]
        else:
            household_ids = [household_id]

        for household_id in household_ids:
            if self.bg:
                self.bg.add_task(self._publish_event, event=event, group_id=group_id, household_id=household_id)
            else:
                self._publish_event(event, group_id, household_id)

    @classmethod
    def as_dependency(
        cls,
        bg: BackgroundTasks,
        session=Depends(generate_session),
    ):
        """Convenience method to use as a dependency in FastAPI routes"""
        return cls(bg, session)
