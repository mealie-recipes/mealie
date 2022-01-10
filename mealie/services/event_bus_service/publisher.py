from typing import Protocol

import apprise

from mealie.services.event_bus_service.event_bus_service import EventBusMessage


class PublisherLike(Protocol):
    def publish(self, event: EventBusMessage, notification_urls: list[str]):
        ...


class ApprisePublisher:
    def __init__(self, hard_fail=False) -> None:
        asset = apprise.AppriseAsset(
            async_mode=True,
            image_url_mask="https://raw.githubusercontent.com/hay-kot/mealie/dev/frontend/public/img/icons/android-chrome-maskable-512x512.png",
        )
        self.apprise = apprise.Apprise(asset=asset)
        self.hard_fail = hard_fail

    def publish(self, event: EventBusMessage, notification_urls: list[str]):
        for dest in notification_urls:
            status = self.apprise.add(dest)

            if not status and self.hard_fail:
                raise Exception("Apprise URL Add Failed")

        self.apprise.notify(title=event.title, body=event.body)
