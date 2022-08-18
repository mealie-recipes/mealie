from typing import Protocol

import apprise

from mealie.services.event_bus_service.event_types import Event


class PublisherLike(Protocol):
    def publish(self, event: Event, notification_urls: list[str]):
        ...


class ApprisePublisher:
    def __init__(self, hard_fail=False) -> None:
        asset = apprise.AppriseAsset(
            async_mode=True,
            image_url_mask="https://raw.githubusercontent.com/hay-kot/mealie/dev/frontend/public/img/icons/android-chrome-maskable-512x512.png",
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
