import http.server
import ipaddress
import socket
import threading

import httpx
import pytest
from curl_cffi import CurlOpt

from mealie.pkgs import safehttp
from mealie.pkgs.safehttp import transport as safehttp_transport
from mealie.pkgs.safehttp.transport import (
    AsyncSafeTransport,
    InvalidDomainError,
    SafeTransport,
    is_blocked_ip,
)


def _request(url: str) -> httpx.Request:
    return httpx.Request("GET", url)


def _patch_resolver(monkeypatch, ips: list[str]) -> None:
    def fake_getaddrinfo(host, port, *args, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port)) for ip in ips]

    monkeypatch.setattr(safehttp_transport.socket, "getaddrinfo", fake_getaddrinfo)


@pytest.mark.parametrize(
    ("ip", "blocked"),
    [
        ("8.8.8.8", False),
        ("2606:4700:4700::1111", False),
        ("10.0.0.1", True),
        ("172.16.5.5", True),
        ("192.168.1.1", True),
        ("127.0.0.1", True),
        ("169.254.169.254", True),  # cloud metadata / link-local
        ("100.64.0.1", True),  # CGNAT, not covered by is_private on all versions
        ("0.0.0.0", True),
        ("224.0.0.1", True),  # multicast
        ("::1", True),
        ("fe80::1", True),
        ("fc00::1", True),
        ("::ffff:127.0.0.1", True),  # IPv4-mapped loopback
    ],
)
def test_is_blocked_ip(ip: str, blocked: bool):
    assert is_blocked_ip(ipaddress.ip_address(ip)) is blocked


def test_blocks_host_resolving_to_private(monkeypatch):
    _patch_resolver(monkeypatch, ["10.0.0.5"])
    transport = AsyncSafeTransport()
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("https://evil.example/"))


def test_allows_public_host_and_returns_pin(monkeypatch):
    _patch_resolver(monkeypatch, ["93.184.216.34"])
    transport = AsyncSafeTransport()
    resolve = transport._validate(_request("https://example.test/path"))
    assert resolve == ["example.test:443:93.184.216.34"]


def test_pin_covers_all_resolved_addresses(monkeypatch):
    _patch_resolver(monkeypatch, ["93.184.216.34", "93.184.216.35"])
    transport = AsyncSafeTransport()
    resolve = transport._validate(_request("http://example.test/"))
    assert resolve == ["example.test:80:93.184.216.34", "example.test:80:93.184.216.35"]


def test_rejects_when_any_resolved_address_is_unsafe(monkeypatch):
    # one public, one private -> reject the whole request
    _patch_resolver(monkeypatch, ["93.184.216.34", "127.0.0.1"])
    transport = AsyncSafeTransport()
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("https://mixed.example/"))


def test_ip_literal_public_needs_no_pin():
    transport = AsyncSafeTransport()
    assert transport._validate(_request("https://93.184.216.34/")) is None


def test_ip_literal_metadata_blocked():
    transport = AsyncSafeTransport()
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("http://169.254.169.254/latest/meta-data/"))


def test_ipv6_resolution_is_validated(monkeypatch):
    _patch_resolver(monkeypatch, ["::1"])
    transport = AsyncSafeTransport()
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("https://v6.example/"))


def test_allow_list_bypasses_block(monkeypatch):
    _patch_resolver(monkeypatch, ["10.0.0.5"])
    transport = AsyncSafeTransport(allow_hosts=["internal.example"])
    resolve = transport._validate(_request("https://internal.example/"))
    assert resolve == ["internal.example:443:10.0.0.5"]


def test_allow_list_cidr_bypasses_block(monkeypatch):
    _patch_resolver(monkeypatch, ["10.1.2.3"])
    transport = AsyncSafeTransport(allow_hosts=["10.0.0.0/8"])
    assert transport._validate(_request("https://internal.example/")) == ["internal.example:443:10.1.2.3"]


def test_deny_list_overrides_allow(monkeypatch):
    _patch_resolver(monkeypatch, ["93.184.216.34"])
    transport = AsyncSafeTransport(allow_hosts=["blocked.example"], deny_hosts=["blocked.example"])
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("https://blocked.example/"))


def test_deny_list_blocks_public_host(monkeypatch):
    _patch_resolver(monkeypatch, ["93.184.216.34"])
    transport = AsyncSafeTransport(deny_hosts=["93.184.216.0/24"])
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("https://public.example/"))


def test_unresolvable_host_is_rejected(monkeypatch):
    def boom(host, port, *args, **kwargs):
        raise socket.gaierror("no such host")

    monkeypatch.setattr(safehttp_transport.socket, "getaddrinfo", boom)
    transport = AsyncSafeTransport()
    with pytest.raises(InvalidDomainError):
        transport._validate(_request("https://nope.invalid/"))


class _LocalServer:
    def __init__(self):
        class Handler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

            def do_POST(self):
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")

            def log_message(self, *args):
                pass

        self.server = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        # `shutdown` only stops the serve_forever loop; without `server_close` the listening
        # socket stays open and pytest fails the test on the resulting ResourceWarning.
        self.server.shutdown()
        self.thread.join()
        self.server.server_close()


@pytest.mark.asyncio
async def test_async_transport_pins_connection_to_validated_ip(monkeypatch):
    with _LocalServer() as server:
        # host does not really resolve to localhost; the resolver + pin make it so
        _patch_resolver(monkeypatch, ["127.0.0.1"])
        transport = AsyncSafeTransport(allow_hosts=["pinned.example"])
        async with httpx.AsyncClient(transport=transport) as client:
            resp = await client.get(f"http://pinned.example:{server.port}/")
        assert resp.status_code == 200
        assert resp.text == "OK"


def test_sync_post_blocks_loopback_by_default():
    with _LocalServer() as server:
        with pytest.raises(InvalidDomainError):
            safehttp.post(f"http://127.0.0.1:{server.port}/", json={"x": 1})


def test_sync_post_allows_configured_host():
    with _LocalServer() as server:
        resp = safehttp.post(
            f"http://127.0.0.1:{server.port}/",
            json={"x": 1},
            allow_hosts=["127.0.0.1"],
        )
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Proxy handling
# ---------------------------------------------------------------------------
def test_noproxy_is_set_when_no_proxy_is_configured():
    """
    Without this, curl silently honors ambient HTTP_PROXY/HTTPS_PROXY -- and a proxied request
    is resolved by the proxy, so the connection pin would no longer apply.
    """
    transport = SafeTransport()
    assert transport._session.curl_options[CurlOpt.NOPROXY] == "*"


def test_noproxy_is_cleared_when_a_proxy_is_configured():
    """An explicitly configured proxy must apply to every host, env vars notwithstanding."""
    transport = SafeTransport(proxy="http://proxy:8080")
    assert transport._session.curl_options[CurlOpt.NOPROXY] == ""


def test_pin_and_proxy_options_coexist(monkeypatch):
    """Applying the pin must not clobber the proxy option living in the same mapping."""
    _patch_resolver(monkeypatch, ["93.184.216.34"])
    transport = SafeTransport(proxy="http://proxy:8080")

    transport._apply_pin(transport._validate(_request("https://example.test/")))

    options = transport._session.curl_options
    assert options[CurlOpt.RESOLVE] == ["example.test:443:93.184.216.34"]
    assert options[CurlOpt.NOPROXY] == ""
