import json
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from fastapi.encoders import jsonable_encoder
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.repos.repository_factory import AllRepositories
from mealie.schema.group.group_events import GroupEventNotifierPrivate

from .event_types import Event
from .publisher import ApprisePublisher, PublisherLike


class EventListenerBase:
    def __init__(self, session: Session, group_id: UUID4, publisher: PublisherLike) -> None:
        self.session = session
        self.group_id = group_id
        self.publisher = publisher

    def get_subscribers(self, event: Event) -> list:
        """Get a list of all subscribers to this event"""
        ...

    def publish_to_subscribers(self, event: Event, subscribers: list) -> None:
        """Publishes the event to all subscribers"""
        ...


class AppriseEventListener(EventListenerBase):
    def __init__(self, session: Session, group_id: UUID4) -> None:
        super().__init__(session, group_id, ApprisePublisher())

    def get_subscribers(self, event: Event) -> list[str]:
        repos = AllRepositories(self.session)

        notifiers: list[GroupEventNotifierPrivate] = repos.group_event_notifier.by_group(  # type: ignore
            self.group_id
        ).multi_query({"enabled": True}, override_schema=GroupEventNotifierPrivate)

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
            "timestamp": event.timestamp.isoformat(),
        }

        return [
            # We use query params to add custom key: value pairs to the Apprise payload by prepending the key with ":".
            AppriseEventListener.merge_query_parameters(url, {f":{k}": v for k, v in params.items()})
            # only certain endpoints support the custom key: value pairs, so we only apply them to those endpoints
            if AppriseEventListener.is_custom_url(url) else url
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
