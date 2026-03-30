from typing import Protocol

import apprise
import httpx
from fastapi.encoders import jsonable_encoder

from mealie.pkgs import safehttp
from mealie.services.event_bus_service.event_types import Event
import logging

logger = logging.getLogger(__name__)


class PublisherLike(Protocol):
    async def publish(self, event: Event, notification_urls: list[str]): ...


class ApprisePublisher:
    def __init__(self, hard_fail=False) -> None:
        asset = apprise.AppriseAsset(
            async_mode=True,
            image_url_mask="https://raw.githubusercontent.com/mealie-recipes/mealie/9571816ac4eed5beacfc0abf6c03eff1427fd0eb/frontend/static/icons/android-chrome-maskable-512x512.png",
        )
        self.apprise = apprise.Apprise(asset=asset)
        self.hard_fail = hard_fail

    def publish(self, event: Event, notification_urls: list[str]):
        """Publishses a list of notification URLs"""

        tags = []
        for dest in notification_urls:
            # we tag the url so it only sends each notification once
            tag = str(event.event_id)
            tags.append(tag)

            status = self.apprise.add(dest, tag=tag)

            if not status and self.hard_fail:
                raise Exception("Apprise URL Add Failed")

        self.apprise.notify(title=event.message.title, body=event.message.body, tag=tags)


class WebhookPublisher:
    def __init__(self, hard_fail=False) -> None:
        self.hard_fail = hard_fail

    async def publish(self, event: Event, notification_urls: list[str]):
        event_payload = jsonable_encoder(event)
        for url in notification_urls:
            async with httpx.AsyncClient(transport=safehttp.AsyncSafeTransport()) as client:
                try:
                    r = await client.post(url, json=event_payload, timeout=15)
                    if self.hard_fail:
                        r.raise_for_status()
                except safehttp.InvalidDomainError:
                    logger.warning(f"Blocked SSRF attempt to internal URL: {url}")
                    if self.hard_fail:
                        raise
                    continue
