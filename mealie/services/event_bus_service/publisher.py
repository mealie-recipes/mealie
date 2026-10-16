from typing import Protocol
from urllib.parse import urlsplit

from fastapi.encoders import jsonable_encoder

from mealie.services.event_bus_service.event_types import Event

# Apprise schemes that POST/GET an arbitrary user-supplied host, the same way the Webhooks
# feature does - as opposed to e.g. "discord://" or "slack://", where the URL's netloc is a
# token/ID for a fixed, hardcoded API host, not a network target. Only these are SSRF-relevant:
# Apprise has no safehttp equivalent of its own, so without this check any of these schemes
# would let a user reach any host/port the server can, with the response surfaced via the
# notifier's "test" endpoint.
#
# Also the single source of truth for AppriseEventListener.is_custom_url, which identifies the
# same schemes for an unrelated reason (whether to append Mealie's custom query params).
CUSTOM_ENDPOINT_SCHEMES = {"json", "jsons", "xml", "xmls", "form", "forms"}


class PublisherLike(Protocol):
    def publish(self, event: Event, notification_urls: list[str]): ...


class ApprisePublisher:
    def __init__(self, hard_fail=False) -> None:
        import apprise

        asset = apprise.AppriseAsset(
            async_mode=True,
            image_url_mask="https://raw.githubusercontent.com/mealie-recipes/mealie/9571816ac4eed5beacfc0abf6c03eff1427fd0eb/frontend/static/icons/android-chrome-maskable-512x512.png",
        )
        self.apprise = apprise.Apprise(asset=asset)
        self.hard_fail = hard_fail

    @staticmethod
    def _assert_safe_destination(dest: str) -> None:
        from mealie.core.config import get_app_settings
        from mealie.pkgs import safehttp

        parts = urlsplit(dest)
        scheme = parts.scheme.lower()
        if scheme not in CUSTOM_ENDPOINT_SCHEMES or not parts.hostname:
            return

        settings = get_app_settings()
        port = parts.port or (443 if scheme in ("jsons", "xmls", "forms") else 80)
        safehttp.resolve_and_validate_host(
            parts.hostname,
            port,
            allow_hosts=settings.http_allow_list,
            deny_hosts=settings.http_disallow_list,
        )

    def publish(self, event: Event, notification_urls: list[str]):
        """Publishses a list of notification URLs"""

        tags = []
        for dest in notification_urls:
            self._assert_safe_destination(dest)

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

    def publish(self, event: Event, notification_urls: list[str]):
        from mealie.core.config import get_app_settings
        from mealie.pkgs import safehttp

        event_payload = jsonable_encoder(event)
        settings = get_app_settings()
        for url in notification_urls:
            r = safehttp.post(
                url,
                json=event_payload,
                timeout=15,
                allow_hosts=settings.http_allow_list,
                deny_hosts=settings.http_disallow_list,
            )
            if self.hard_fail:
                r.raise_for_status()
