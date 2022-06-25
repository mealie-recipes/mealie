from enum import Enum
from typing import Any
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit
from uuid import uuid4

from fastapi import BackgroundTasks, Depends
from pydantic import UUID4

from mealie.db.db_setup import generate_session
from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_events import GroupEventNotifierPrivate

from .message_types import EventBusMessage, EventTypes
from .publisher import ApprisePublisher, PublisherLike


class EventTrigger(Enum):
    generic = "generic"
    integration = "integration"


class EventSource:
    id: UUID4
    actor: str | int | UUID4
    event_trigger: EventTrigger
    event_trigger_id: str
    event_type: str
    item_type: str
    item_id: UUID4 | int
    kwargs: dict[str, Any]

    def __init__(
        self,
        actor: str | int | UUID4,
        event_trigger: EventTrigger,
        event_type: str,
        item_type: str,
        item_id: UUID4 | int,
        event_trigger_id: str | None = None,
        **kwargs,
    ) -> None:
        if event_trigger_id is None:
            event_trigger_id = ""

        self.id = uuid4()
        self.actor = actor
        self.event_trigger = event_trigger
        self.event_trigger_id = event_trigger_id
        self.event_type = event_type
        self.item_type = item_type
        self.item_id = item_id
        self.kwargs = kwargs

    def dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "actor": self.actor,
            "event_trigger": self.event_trigger.value,
            "event_trigger_id": self.event_trigger_id,
            "event_type": self.event_type,
            "item_type": self.item_type,
            "item_id": self.item_id,
            **self.kwargs,
        }


class EventBusService:
    def __init__(self, bg: BackgroundTasks, session=Depends(generate_session)) -> None:
        self.bg = bg
        self._publisher = ApprisePublisher
        self.session = session
        self.group_id: UUID4 | None = None

    @property
    def publisher(self) -> PublisherLike:
        return self._publisher()

    def get_urls(self, event_type: EventTypes) -> list[str]:
        repos = AllRepositories(self.session)

        notifiers: list[GroupEventNotifierPrivate] = repos.group_event_notifier.by_group(  # type: ignore
            self.group_id
        ).multi_query({"enabled": True}, override_schema=GroupEventNotifierPrivate)

        return [notifier.apprise_url for notifier in notifiers if getattr(notifier.options, event_type.name)]

    def dispatch(
        self,
        group_id: UUID4,
        event_type: EventTypes,
        msg: str = "",
        event_source: EventSource | None = None,
    ) -> None:
        self.group_id = group_id

        def _dispatch(event_source: EventSource = None):
            if urls := self.get_urls(event_type):
                if event_source:
                    urls = EventBusService.update_urls_with_event_source(urls, event_source)

                self.publisher.publish(EventBusMessage.from_type(event_type, body=msg), urls)

        if dispatch_task := _dispatch(event_source=event_source):
            self.bg.add_task(dispatch_task)

    def test_publisher(self, url: str) -> None:
        self.bg.add_task(
            self.publisher.publish,
            event=EventBusMessage.from_type(EventTypes.test_message, body="This is a test event."),
            notification_urls=[url],
        )

    @staticmethod
    def update_urls_with_event_source(urls: list[str], event_source: EventSource):
        return [
            # We use query params to add custom key: value pairs to the Apprise payload by prepending the key with ":".
            EventBusService.merge_query_parameters(url, {f":{k}": v for k, v in event_source.dict().items()})
            # only certain endpoints support the custom key: value pairs, so we only apply them to those endpoints
            if EventBusService.is_custom_url(url) else url
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
        return url.split(":", 1)[0].lower() in ["form", "forms", "json", "jsons", "xml", "xmls"]
