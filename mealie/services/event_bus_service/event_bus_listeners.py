import contextlib
import json
from abc import ABC, abstractmethod
from collections.abc import Generator
from datetime import UTC, datetime
from typing import cast
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.orm.session import Session

from mealie.db.db_setup import session_context
from mealie.db.models.household.webhooks import GroupWebhooksModel
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.household.group_events import GroupEventNotifierPrivate
from mealie.schema.household.webhook import ReadWebhook

from .event_types import Event, EventDocumentType, EventTypes, EventWebhookData
from .publisher import ApprisePublisher, PublisherLike, WebhookPublisher


class EventListenerBase(ABC):
    _session: Session | None = None
    _repos: AllRepositories | None = None

    def __init__(self, group_id: UUID4, household_id: UUID4, publisher: PublisherLike) -> None:
        self.group_id = group_id
        self.household_id = household_id
        self.publisher = publisher
        self._session = None
        self._repos = None

    @abstractmethod
    def get_subscribers(self, event: Event) -> list:
        """Get a list of all subscribers to this event"""
        ...

    @abstractmethod
    def publish_to_subscribers(self, event: Event, subscribers: list) -> None:
        """Publishes the event to all subscribers"""
        ...

    @contextlib.contextmanager
    def ensure_session(self) -> Generator[Session, None, None]:
        """
        ensure_session ensures that a session is available for the caller by checking if a session
        was provided during construction, and if not, creating a new session with the `with_session`
        function and closing it when the context manager exits.

        This is _required_ when working with sessions inside an event bus listener where the listener
        may be constructed during a request where the session is provided by the request, but the when
        run as a scheduled task, the session is not provided and must be created.
        """
        if self._session is None:
            with session_context() as session:
                self._session = session
                yield self._session
        else:
            yield self._session

    @contextlib.contextmanager
    def ensure_repos(self, group_id: UUID4, household_id: UUID4) -> Generator[AllRepositories, None, None]:
        if self._repos is None:
            with self.ensure_session() as session:
                self._repos = AllRepositories(session, group_id=group_id, household_id=household_id)
                yield self._repos
        else:
            yield self._repos


class AppriseEventListener(EventListenerBase):
    def __init__(self, group_id: UUID4, household_id: UUID4) -> None:
        super().__init__(group_id, household_id, ApprisePublisher())

    def get_subscribers(self, event: Event) -> list[str]:
        with self.ensure_repos(self.group_id, self.household_id) as repos:
            notifiers: list[GroupEventNotifierPrivate] = repos.group_event_notifier.multi_query(
                {"enabled": True}, override_schema=GroupEventNotifierPrivate
            )

            urls = [notifier.apprise_url for notifier in notifiers if getattr(notifier.options, event.event_type.name)]
            urls = AppriseEventListener.update_urls_with_event_data(urls, event)

        return urls

    def publish_to_subscribers(self, event: Event, subscribers: list[str]) -> None:
        self.publisher.publish(event, subscribers)

    @staticmethod
    def update_urls_with_event_data(urls: list[str], event: Event):
        params = {
            "event_type": event.event_type.name,
            "integration_id": event.integration_id,
            "document_data": json.dumps(jsonable_encoder(event.document_data)),
            "event_id": str(event.event_id),
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }

        return [
            # We use query params to add custom key: value pairs to the Apprise payload by prepending the key with ":".
            (
                AppriseEventListener.merge_query_parameters(url, {f":{k}": v for k, v in params.items()})
                # only certain endpoints support the custom key: value pairs, so we only apply them to those endpoints
                if AppriseEventListener.is_custom_url(url)
                else url
            )
            for url in urls
        ]

    @staticmethod
    def merge_query_parameters(url: str, params: dict):
        scheme, netloc, path, query_string, fragment = urlsplit(url)

        # merge query params
        query_params = parse_qs(query_string)
        query_params.update(params)
        new_query_string = urlencode(query_params, doseq=True)

        return urlunsplit((scheme, netloc, path, new_query_string, fragment))

    @staticmethod
    def is_custom_url(url: str):
        return url.split(":", 1)[0].lower() in [
            "form",
            "forms",
            "json",
            "jsons",
            "xml",
            "xmls",
        ]


class WebhookEventListener(EventListenerBase):
    def __init__(self, group_id: UUID4, household_id: UUID4) -> None:
        super().__init__(group_id, household_id, WebhookPublisher())

    def get_subscribers(self, event: Event) -> list[ReadWebhook]:
        # we only care about events that contain webhook information
        if not (event.event_type == EventTypes.webhook_task and isinstance(event.document_data, EventWebhookData)):
            return []

        scheduled_webhooks = self.get_scheduled_webhooks(
            event.document_data.webhook_start_dt, event.document_data.webhook_end_dt
        )
        return scheduled_webhooks

    def publish_to_subscribers(self, event: Event, subscribers: list[ReadWebhook]) -> None:
        with self.ensure_repos(self.group_id, self.household_id) as repos:
            if event.document_data.document_type == EventDocumentType.mealplan:
                webhook_data = cast(EventWebhookData, event.document_data)
                meal_repo = repos.meals
                meal_data = meal_repo.get_meals_by_date_range(
                    webhook_data.webhook_start_dt, webhook_data.webhook_end_dt
                )
                if meal_data:
                    webhook_data.webhook_body = meal_data
                    self.publisher.publish(event, [webhook.url for webhook in subscribers])

    def get_scheduled_webhooks(self, start_dt: datetime, end_dt: datetime) -> list[ReadWebhook]:
        """Fetches all scheduled webhooks from the database"""
        with self.ensure_session() as session:
            stmt = select(GroupWebhooksModel).where(
                GroupWebhooksModel.enabled == True,  # noqa: E712 - required for SQLAlchemy comparison
                GroupWebhooksModel.scheduled_time > start_dt.astimezone(UTC).time(),
                GroupWebhooksModel.scheduled_time <= end_dt.astimezone(UTC).time(),
                GroupWebhooksModel.group_id == self.group_id,
                GroupWebhooksModel.household_id == self.household_id,
            )
            return session.execute(stmt).scalars().all()
