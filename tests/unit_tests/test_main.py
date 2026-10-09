"""Startup binding for the production `mealie` command.

The ASGI app below stays in this test module. Production startup serves `mealie.app:app`.
"""

import errno
import http.client
import os
import signal
import socket
import subprocess
import sys
import threading
import time
from collections.abc import Iterator
from pathlib import Path

import pytest
from uvicorn.config import STARTUP_FAILURE, Config

from mealie.core.config import get_app_settings
from mealie.core.logger.config import log_config
from mealie.main import (
    _ASGI_APP,
    _run_server,
    _serve_sockets,
    create_wildcard_listener,
    main,
)

_DUAL_FAMILY_SKIP = "IPv6 dual-stack loopback is unavailable on this host; dual-family listen was not verified"
_REPO_ROOT = Path(__file__).resolve().parents[2]


async def asgi_app(scope, receive, send):
    """Minimal HTTP app used to prove the production listener accepts real connections."""
    if scope["type"] != "http":
        return

    while True:
        message = await receive()
        if message["type"] == "http.disconnect":
            return
        if message["type"] == "http.request" and not message.get("more_body", False):
            break

    body = b"ok"
    await send(
        {
            "type": "http.response.start",
            "status": 200,
            "headers": [
                (b"content-type", b"text/plain"),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


def _ipv6_loopback_available() -> bool:
    try:
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as probe:
            probe.bind(("::1", 0))
    except OSError:
        return False
    return True


def _dual_family_available() -> bool:
    return bool(socket.has_dualstack_ipv6()) and _ipv6_loopback_available()


def _routable_ipv4() -> str | None:
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as probe:
        try:
            probe.connect(("192.0.2.1", 9))
        except OSError:
            return None
        address = probe.getsockname()[0]
    if address.startswith("127."):
        return None
    return address


def _http_get(host: str, port: int, timeout: float = 2) -> bytes:
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        connection.request("GET", "/")
        response = connection.getresponse()
        body = response.read()
        status = response.status
    finally:
        connection.close()
    if status != 200:
        raise AssertionError(f"{host}:{port} returned HTTP {status}")
    return body


def _http_get_when_ready(host: str, port: int, proc: subprocess.Popen[bytes] | None, timeout: float = 30) -> bytes:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if proc is not None and proc.poll() is not None:
            break
        try:
            return _http_get(host, port)
        except (OSError, http.client.HTTPException) as exc:
            last_error = exc
            time.sleep(0.05)
    raise AssertionError(f"{host}:{port} did not serve GET within {timeout}s ({last_error})")


def _assert_refused(host: str, port: int) -> None:
    try:
        with socket.create_connection((host, port), timeout=0.5):
            raise AssertionError(f"{host}:{port} accepted a connection")
    except AssertionError:
        raise
    except OSError as exc:
        assert exc.errno == errno.ECONNREFUSED, exc


def _assert_port_is_free(port: int) -> None:
    _assert_refused("127.0.0.1", port)
    with socket.create_server(("127.0.0.1", port)) as rebound:
        assert rebound.getsockname()[1] == port


def _stop_process_group(proc: subprocess.Popen[bytes]) -> None:
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait(timeout=5)


class _ManagedServer:
    """Bounded child process that runs shipped listener code against ``asgi_app``."""

    def __init__(self, tmp_path: Path, **env_extra: str) -> None:
        self.port_file = tmp_path / "port"
        self.log_path = tmp_path / "server.log"
        self.log_handle = self.log_path.open("w")
        env = os.environ.copy()
        env.update(env_extra)
        env["MEALIE_LISTENER_PORT_FILE"] = str(self.port_file)
        env["TESTING"] = "True"
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONPATH"] = os.pathsep.join(filter(None, [str(_REPO_ROOT), env.get("PYTHONPATH", "")]))
        self.proc = subprocess.Popen(
            [sys.executable, "-c", "from tests.unit_tests.test_main import _child_server; _child_server()"],
            cwd=_REPO_ROOT,
            env=env,
            stdout=self.log_handle,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )

    def log_text(self) -> str:
        self.log_handle.flush()
        if not self.log_path.exists():
            return ""
        return self.log_path.read_text(errors="replace")[-4000:]

    def failure(self, message: str) -> AssertionError:
        code = self.proc.poll()
        return AssertionError(f"{message} (exit={code})\n{self.log_text()}")

    def wait_port(self, timeout: float = 30) -> tuple[int, str]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.port_file.exists():
                text = self.port_file.read_text().strip()
                if text:
                    port_text, _, family = text.partition(" ")
                    return int(port_text), family
            if self.proc.poll() is not None:
                raise self.failure("server exited before publishing its port")
            time.sleep(0.05)
        raise self.failure("timed out waiting for the listening port")

    def close(self) -> None:
        try:
            _stop_process_group(self.proc)
        finally:
            self.log_handle.close()

    def __enter__(self) -> _ManagedServer:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()


def _child_server() -> None:
    mode = os.environ["MEALIE_LISTENER_MODE"]
    workers = int(os.environ.get("MEALIE_LISTENER_WORKERS", "1"))
    port_file = Path(os.environ["MEALIE_LISTENER_PORT_FILE"])
    max_requests = os.environ.get("MEALIE_LISTENER_MAX_REQUESTS")
    options: dict[str, object] = {
        "log_level": "error",
        "log_config": None,
        "workers": workers,
        "ws": "websockets-sansio",
        "forwarded_allow_ips": "*",
        "lifespan": "off",
        "access_log": False,
    }
    if max_requests:
        options["limit_max_requests"] = int(max_requests)

    app = "tests.unit_tests.test_main:asgi_app"
    if mode == "fail":
        app = "tests.unit_tests.test_main:missing_asgi_app"

    if mode == "explicit":
        port = int(os.environ["MEALIE_LISTENER_PORT"])
        port_file.write_text(f"{port}\n")
        _run_server(app, host=os.environ["MEALIE_LISTENER_HOST"], port=port, **options)
        return

    if mode == "fallback":
        socket.has_dualstack_ipv6 = lambda: False  # type: ignore[method-assign]

    listener = create_wildcard_listener(0)
    bound_port = listener.getsockname()[1]
    family = "AF_INET6" if listener.family == socket.AF_INET6 else "AF_INET"
    port_file.write_text(f"{bound_port} {family}\n")
    _serve_sockets(Config(app, host="", port=bound_port, **options), [listener])


def _free_loopback_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


@pytest.fixture
def restored_settings_cache() -> Iterator[None]:
    get_app_settings.cache_clear()
    yield
    get_app_settings.cache_clear()


def test_minimal_asgi_app_stays_in_the_test_module():
    assert asgi_app.__module__ == "tests.unit_tests.test_main"
    assert create_wildcard_listener.__module__ == "mealie.main"
    assert _ASGI_APP == "mealie.app:app"


@pytest.mark.parametrize("host", ["0.0.0.0", "127.0.0.1", "::", "::1"])
def test_explicit_api_host_reaches_uvicorn_unchanged(
    host: str, monkeypatch: pytest.MonkeyPatch, restored_settings_cache: None
):
    monkeypatch.setenv("API_HOST", host)
    get_app_settings.cache_clear()
    captured: dict[str, object] = {}

    def fake_run(app: str, **kwargs: object) -> None:
        captured["app"] = app
        captured["kwargs"] = kwargs

    def forbid_wildcard(port: int) -> socket.socket:
        raise AssertionError(f"explicit host {host} opened a wildcard listener on {port}")

    monkeypatch.setattr("mealie.main.uvicorn.run", fake_run)
    monkeypatch.setattr("mealie.main.create_wildcard_listener", forbid_wildcard)

    parsed = get_app_settings()
    assert parsed.API_HOST == host
    main()

    kwargs = captured["kwargs"]
    assert isinstance(kwargs, dict)
    assert captured["app"] == "mealie.app:app"
    assert kwargs["host"] == host
    assert kwargs["port"] == parsed.API_PORT
    assert kwargs["workers"] == parsed.WORKERS
    assert kwargs["ws"] == "websockets-sansio"
    assert kwargs["forwarded_allow_ips"] == parsed.HOST_IP
    assert kwargs["ssl_keyfile"] == parsed.TLS_PRIVATE_KEY_PATH
    assert kwargs["ssl_certfile"] == parsed.TLS_CERTIFICATE_PATH
    assert kwargs["log_level"] == parsed.LOG_LEVEL.lower()
    assert kwargs["log_config"] == log_config()


def test_automatic_binding_preserves_server_options(monkeypatch: pytest.MonkeyPatch, restored_settings_cache: None):
    monkeypatch.setenv("API_HOST", "")
    monkeypatch.setenv("API_PORT", "9123")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("HOST_IP", "10.9.8.7")
    monkeypatch.setenv("TLS_CERTIFICATE_PATH", "/tmp/mealie-cert.pem")
    monkeypatch.setenv("TLS_PRIVATE_KEY_PATH", "/tmp/mealie-key.pem")
    monkeypatch.setenv("UVICORN_WORKERS", "2")
    monkeypatch.setenv("WORKER_PER_CORE", "1")
    get_app_settings.cache_clear()

    captured: dict[str, object] = {}

    class _DummySocket:
        def __init__(self) -> None:
            self.closed = False

        def close(self) -> None:
            self.closed = True

    dummy = _DummySocket()

    def fake_listener(port: int) -> _DummySocket:
        captured["port"] = port
        return dummy

    def fake_serve(config: Config, sockets: list[socket.socket]) -> None:
        captured["config"] = config
        captured["sockets"] = sockets
        for listener in sockets:
            listener.close()

    def forbid_run(*args: object, **kwargs: object) -> None:
        raise AssertionError("automatic binding used uvicorn.run()")

    monkeypatch.setattr("mealie.main.create_wildcard_listener", fake_listener)
    monkeypatch.setattr("mealie.main._serve_sockets", fake_serve)
    monkeypatch.setattr("mealie.main.uvicorn.run", forbid_run)

    main()

    config = captured["config"]
    assert isinstance(config, Config)
    assert captured["port"] == 9123
    assert captured["sockets"] == [dummy]
    assert dummy.closed
    assert config.app == "mealie.app:app"
    assert config.host == ""
    assert config.port == 9123
    assert config.workers == 2
    assert config.log_level == "warning"
    assert config.ws == "websockets-sansio"
    assert config.forwarded_allow_ips == "10.9.8.7"
    assert config.ssl_certfile == "/tmp/mealie-cert.pem"
    assert config.ssl_keyfile == "/tmp/mealie-key.pem"
    assert config.log_config == log_config()


def test_dualstack_socket_disables_ipv6_only_when_supported():
    if not _dual_family_available():
        pytest.skip(_DUAL_FAMILY_SKIP)

    listener = create_wildcard_listener(0)
    try:
        assert listener.family == socket.AF_INET6
        assert listener.get_inheritable()
        assert listener.getsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY) == 0
        assert listener.getsockname()[0] == "::"
    finally:
        listener.close()


@pytest.mark.parametrize("workers", [1, 2])
def test_automatic_listener_serves_ipv4_and_ipv6(workers: int, tmp_path: Path):
    if not _dual_family_available():
        pytest.skip(_DUAL_FAMILY_SKIP)

    with _ManagedServer(tmp_path, MEALIE_LISTENER_MODE="auto", MEALIE_LISTENER_WORKERS=str(workers)) as server:
        port, family = server.wait_port()
        assert family == "AF_INET6"
        assert _http_get_when_ready("127.0.0.1", port, server.proc) == b"ok"
        assert _http_get_when_ready("::1", port, server.proc) == b"ok"


def test_disabled_dualstack_probe_binds_ipv4_once(monkeypatch: pytest.MonkeyPatch):
    calls: list[int] = []
    real_create_server = socket.create_server

    def spy_create_server(*args: object, **kwargs: object) -> socket.socket:
        family = kwargs.get("family", socket.AF_INET)
        assert isinstance(family, int)
        calls.append(family)
        return real_create_server(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(socket, "has_dualstack_ipv6", lambda: False)
    monkeypatch.setattr(socket, "create_server", spy_create_server)

    listener = create_wildcard_listener(0)
    try:
        assert listener.family == socket.AF_INET
        assert calls == [socket.AF_INET]
    finally:
        listener.close()


def test_ipv4_fallback_serves_ipv4_only(tmp_path: Path):
    if not _ipv6_loopback_available():
        pytest.skip("IPv6 loopback is unavailable; the IPv4-only fallback was not compared with ::1")

    with _ManagedServer(tmp_path, MEALIE_LISTENER_MODE="fallback", MEALIE_LISTENER_WORKERS="1") as server:
        port, family = server.wait_port()
        assert family == "AF_INET"
        assert _http_get_when_ready("127.0.0.1", port, server.proc) == b"ok"
        _assert_refused("::1", port)


@pytest.mark.parametrize("unavailable_errno", [errno.EAFNOSUPPORT, errno.EADDRNOTAVAIL])
def test_ipv6_bind_failure_falls_back_to_ipv4(unavailable_errno: int, monkeypatch: pytest.MonkeyPatch):
    real_create_server = socket.create_server
    calls: list[int] = []

    def spy_create_server(*args: object, **kwargs: object) -> socket.socket:
        family = kwargs.get("family", socket.AF_INET)
        assert isinstance(family, int)
        calls.append(family)
        if family == socket.AF_INET6:
            raise OSError(unavailable_errno, os.strerror(unavailable_errno))
        return real_create_server(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(socket, "has_dualstack_ipv6", lambda: True)
    monkeypatch.setattr(socket, "create_server", spy_create_server)
    listener = create_wildcard_listener(0)
    try:
        assert calls == [socket.AF_INET6, socket.AF_INET]
        assert listener.family == socket.AF_INET
    finally:
        listener.close()


def test_ipv4_fallback_preserves_the_ipv4_bind_error(monkeypatch: pytest.MonkeyPatch):
    calls: list[int] = []

    def fail_create_server(*args: object, **kwargs: object) -> socket.socket:
        family = kwargs.get("family", socket.AF_INET)
        assert isinstance(family, int)
        calls.append(family)
        if family == socket.AF_INET6:
            raise OSError(errno.EAFNOSUPPORT, "Address family not supported by protocol")
        raise OSError(errno.EADDRINUSE, "Address already in use")

    monkeypatch.setattr(socket, "has_dualstack_ipv6", lambda: True)
    monkeypatch.setattr(socket, "create_server", fail_create_server)

    with pytest.raises(OSError) as caught:
        create_wildcard_listener(0)

    assert caught.value.errno == errno.EADDRINUSE
    assert isinstance(caught.value.__cause__, OSError)
    assert caught.value.__cause__.errno == errno.EAFNOSUPPORT
    assert calls == [socket.AF_INET6, socket.AF_INET]


@pytest.mark.parametrize(
    "bind_error",
    [
        PermissionError(errno.EACCES, "Permission denied"),
        OSError(errno.EPERM, "Operation not permitted"),
        OSError(errno.EADDRINUSE, "Address already in use"),
    ],
)
def test_permission_and_address_in_use_are_not_retried(bind_error: OSError, monkeypatch: pytest.MonkeyPatch):
    calls: list[int] = []

    def fail_create_server(*args: object, **kwargs: object) -> socket.socket:
        family = kwargs.get("family", socket.AF_INET)
        assert isinstance(family, int)
        calls.append(family)
        raise bind_error

    monkeypatch.setattr(socket, "has_dualstack_ipv6", lambda: True)
    monkeypatch.setattr(socket, "create_server", fail_create_server)

    with pytest.raises(OSError) as caught:
        create_wildcard_listener(0)

    assert caught.value is bind_error
    assert caught.value.errno == bind_error.errno
    assert calls == [socket.AF_INET6]


def test_occupied_wildcard_port_fails_once_and_does_not_leak(monkeypatch: pytest.MonkeyPatch):
    holder = socket.create_server(("0.0.0.0", 0))
    port = holder.getsockname()[1]
    holders = [holder]
    if socket.has_dualstack_ipv6():
        try:
            holders.append(socket.create_server(("::", port), family=socket.AF_INET6, dualstack_ipv6=True))
        except OSError:
            pass

    calls: list[int] = []
    real_create_server = socket.create_server

    def spy_create_server(*args: object, **kwargs: object) -> socket.socket:
        family = kwargs.get("family", socket.AF_INET)
        assert isinstance(family, int)
        calls.append(family)
        return real_create_server(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(socket, "create_server", spy_create_server)
    try:
        with pytest.raises(OSError) as caught:
            create_wildcard_listener(port)
        assert caught.value.errno == errno.EADDRINUSE
        assert len(calls) == 1
    finally:
        for held in holders:
            held.close()

    _assert_port_is_free(port)


def test_normal_shutdown_closes_owned_socket():
    listener = create_wildcard_listener(0)
    port = listener.getsockname()[1]
    config = Config(
        "tests.unit_tests.test_main:asgi_app",
        host="",
        port=port,
        workers=1,
        log_level="error",
        log_config=None,
        lifespan="off",
        access_log=False,
        limit_max_requests=1,
    )
    thread = threading.Thread(target=_serve_sockets, args=(config, [listener]), daemon=True)
    thread.start()
    try:
        assert _http_get_when_ready("127.0.0.1", port, None, timeout=10) == b"ok"
    finally:
        thread.join(timeout=5)

    assert not thread.is_alive()
    assert listener.fileno() == -1
    _assert_port_is_free(port)


def test_startup_exception_closes_owned_socket(monkeypatch: pytest.MonkeyPatch):
    listener = create_wildcard_listener(0)
    port = listener.getsockname()[1]

    def explode(self: object, sockets: list[socket.socket] | None = None) -> None:
        raise RuntimeError("startup failed")

    monkeypatch.setattr("mealie.main.Server.run", explode)
    config = Config(
        "tests.unit_tests.test_main:asgi_app",
        host="",
        port=port,
        workers=1,
        log_level="error",
        log_config=None,
        lifespan="off",
    )
    with pytest.raises(RuntimeError, match="startup failed"):
        _serve_sockets(config, [listener])

    assert listener.fileno() == -1
    _assert_port_is_free(port)


def test_single_worker_startup_failure_exits_nonzero(tmp_path: Path):
    with _ManagedServer(tmp_path, MEALIE_LISTENER_MODE="fail", MEALIE_LISTENER_WORKERS="1") as server:
        port, _family = server.wait_port()
        try:
            server.proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            raise server.failure("startup failure did not exit") from None
        assert server.proc.returncode == STARTUP_FAILURE, server.log_text()
        _assert_port_is_free(port)


def test_explicit_ipv4_loopback_does_not_listen_on_other_addresses(tmp_path: Path):
    port = _free_loopback_port()
    with _ManagedServer(
        tmp_path,
        MEALIE_LISTENER_MODE="explicit",
        MEALIE_LISTENER_HOST="127.0.0.1",
        MEALIE_LISTENER_PORT=str(port),
        MEALIE_LISTENER_WORKERS="1",
    ) as server:
        published, _family = server.wait_port()
        assert published == port
        assert _http_get_when_ready("127.0.0.1", port, server.proc) == b"ok"
        if _ipv6_loopback_available():
            _assert_refused("::1", port)
        other = _routable_ipv4()
        if other is not None:
            _assert_refused(other, port)
