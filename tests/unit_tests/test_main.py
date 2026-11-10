"""Startup binding for the production `mealie` command."""

import errno
import socket

import pytest
from uvicorn.config import STARTUP_FAILURE
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from mealie.core.config import get_app_settings
from mealie.main import _with_mapped_proxy_ips, create_wildcard_listener, main


class _FakeListener:
    def __init__(self, family: int) -> None:
        self.family = family
        self.closed = False

    def fileno(self) -> int:
        return 42

    def __enter__(self) -> _FakeListener:
        return self

    def __exit__(self, *exc: object) -> None:
        self.closed = True


@pytest.fixture
def use_settings(monkeypatch: pytest.MonkeyPatch):
    """Point mealie.main at settings parsed from the env vars set by the test."""

    def apply(**env: str) -> None:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        get_app_settings.cache_clear()
        monkeypatch.setattr("mealie.main.settings", get_app_settings())

    yield apply
    get_app_settings.cache_clear()


@pytest.fixture
def captured_run(monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    captured: dict[str, object] = {}

    def fake_run(app: str, **kwargs: object) -> None:
        captured["app"] = app
        captured.update(kwargs)

    monkeypatch.setattr("mealie.main.uvicorn.run", fake_run)
    return captured


@pytest.mark.parametrize("host", ["0.0.0.0", "127.0.0.1", "::", "::1"])
def test_explicit_api_host_reaches_uvicorn_unchanged(
    host: str, use_settings, captured_run: dict[str, object], monkeypatch: pytest.MonkeyPatch
):
    use_settings(API_HOST=host, HOST_IP="127.0.0.1")

    def forbid_wildcard(port: int) -> socket.socket:
        raise AssertionError(f"explicit host {host} opened a wildcard listener on {port}")

    monkeypatch.setattr("mealie.main.create_wildcard_listener", forbid_wildcard)
    main()

    assert captured_run["app"] == "mealie.app:app"
    assert captured_run["host"] == host
    assert captured_run["forwarded_allow_ips"] == "127.0.0.1"
    assert "fd" not in captured_run


def test_automatic_binding_hands_uvicorn_the_listener(
    use_settings, captured_run: dict[str, object], monkeypatch: pytest.MonkeyPatch
):
    use_settings(API_HOST="", API_PORT="9123", HOST_IP="127.0.0.1", UVICORN_WORKERS="2", WORKER_PER_CORE="1")
    listener = _FakeListener(socket.AF_INET6)
    ports: list[int] = []
    monkeypatch.setattr("mealie.main.create_wildcard_listener", lambda port: ports.append(port) or listener)
    main()

    assert ports == [9123]
    assert captured_run["fd"] == 42
    assert "host" not in captured_run and "port" not in captured_run
    assert captured_run["workers"] == 2
    assert captured_run["ws"] == "websockets-sansio"
    assert captured_run["forwarded_allow_ips"] == "127.0.0.1,::ffff:127.0.0.1"
    assert listener.closed


def test_ipv4_fallback_listener_keeps_proxy_ips(
    use_settings, captured_run: dict[str, object], monkeypatch: pytest.MonkeyPatch
):
    use_settings(API_HOST="", HOST_IP="10.9.8.7")
    monkeypatch.setattr("mealie.main.create_wildcard_listener", lambda port: _FakeListener(socket.AF_INET))
    main()
    assert captured_run["forwarded_allow_ips"] == "10.9.8.7"


def test_mapped_proxy_ips_are_trusted():
    assert _with_mapped_proxy_ips("*") == "*"
    expanded = _with_mapped_proxy_ips("127.0.0.1,10.42.1.0/24")
    assert expanded == "127.0.0.1,10.42.1.0/24,::ffff:127.0.0.1,::ffff:10.42.1.0/120"
    trusted = ProxyHeadersMiddleware(None, trusted_hosts=expanded).trusted_hosts  # type: ignore[arg-type]
    assert "::ffff:127.0.0.1" in trusted and "::ffff:10.42.1.5" in trusted
    assert "10.42.1.5" in trusted and "203.0.113.7" not in trusted


def test_dualstack_socket_disables_ipv6_only_when_supported():
    if not socket.has_dualstack_ipv6():
        pytest.skip("IPv6 dual-stack is unavailable on this host")
    with create_wildcard_listener(0) as listener:
        assert listener.family == socket.AF_INET6
        assert listener.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY) == 0


@pytest.mark.parametrize("unavailable", [errno.EAFNOSUPPORT, errno.EADDRNOTAVAIL])
def test_ipv6_unavailable_falls_back_to_ipv4(unavailable: int, monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple] = []

    def fake_create_server(address: tuple, **kwargs: object) -> str:
        calls.append(address)
        if address[0] == "::":
            raise OSError(unavailable, "unavailable")
        return "ipv4"

    monkeypatch.setattr("mealie.main.socket.has_dualstack_ipv6", lambda: True)
    monkeypatch.setattr("mealie.main.socket.create_server", fake_create_server)
    assert create_wildcard_listener(9000) == "ipv4"
    assert calls == [("::", 9000), ("0.0.0.0", 9000)]


@pytest.mark.parametrize("error", [errno.EADDRINUSE, errno.EACCES])
def test_address_in_use_and_permission_errors_are_not_retried(error: int, monkeypatch: pytest.MonkeyPatch):
    calls: list[tuple] = []

    def fake_create_server(address: tuple, **kwargs: object) -> None:
        calls.append(address)
        raise OSError(error, "bind failed")

    monkeypatch.setattr("mealie.main.socket.has_dualstack_ipv6", lambda: True)
    monkeypatch.setattr("mealie.main.socket.create_server", fake_create_server)
    with pytest.raises(OSError) as raised:
        create_wildcard_listener(9000)
    assert raised.value.errno == error
    assert calls == [("::", 9000)]


def test_automatic_bind_error_exits_like_uvicorn(
    use_settings, captured_run: dict[str, object], monkeypatch: pytest.MonkeyPatch
):
    use_settings(API_HOST="")

    def occupied(port: int) -> None:
        raise OSError(errno.EADDRINUSE, "Address already in use")

    monkeypatch.setattr("mealie.main.create_wildcard_listener", occupied)
    with pytest.raises(SystemExit) as raised:
        main()
    assert raised.value.code == STARTUP_FAILURE
    assert captured_run == {}
