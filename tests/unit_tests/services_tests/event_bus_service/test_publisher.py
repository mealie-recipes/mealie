import socket

import pytest

from mealie.pkgs.safehttp import InvalidDomainError
from mealie.pkgs.safehttp import transport as safehttp_transport
from mealie.services.event_bus_service.publisher import ApprisePublisher


def _patch_resolver(monkeypatch, ips: list[str]) -> None:
    def fake_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)) for ip in ips]

    monkeypatch.setattr(safehttp_transport.socket, "getaddrinfo", fake_getaddrinfo)


@pytest.mark.parametrize(
    "dest",
    [
        "json://169.254.169.254/latest/meta-data/",
        "jsons://169.254.169.254/latest/meta-data/",
        "xml://169.254.169.254/",
        "xmls://169.254.169.254/",
        "form://169.254.169.254/",
        "forms://169.254.169.254/",
    ],
)
def test_assert_safe_destination_blocks_custom_endpoint_schemes_targeting_metadata(dest: str):
    """Regression test: Apprise's "custom endpoint" schemes (json/xml/form) POST/GET to a
    user-supplied host exactly like the Webhooks feature does, but previously had none of
    safehttp's SSRF protection - a user could target the cloud metadata endpoint or any other
    internal address and get the result reflected via the notifier's "test" action."""
    with pytest.raises(InvalidDomainError):
        ApprisePublisher._assert_safe_destination(dest)


def test_assert_safe_destination_allows_custom_endpoint_targeting_public_host(monkeypatch):
    _patch_resolver(monkeypatch, ["93.184.216.34"])
    # must not raise
    ApprisePublisher._assert_safe_destination("json://example.test/path")


@pytest.mark.parametrize(
    "dest",
    [
        # hardcoded hosted-service schemes: the netloc is a token/channel id, not a network
        # target, so these must be left alone even though they resolve to nothing real.
        # These are shaped like real tokens only loosely - deliberately not real-looking
        # enough to trip secret scanners, since the test doesn't need an authentic one.
        "discord://not-a-real-webhook-id/not-a-real-webhook-token-NNNNNNNNNNNNNNNNNNNNNN",
        "slack://not-a-real-team-id/not-a-real-bot-id/not-a-real-access-token/",
        "tgram://not-a-real-chat-id:not-a-real-bot-token/",
    ],
)
def test_assert_safe_destination_ignores_hosted_service_schemes(dest: str):
    # must not raise, and must not attempt DNS resolution on the token in netloc position
    ApprisePublisher._assert_safe_destination(dest)
