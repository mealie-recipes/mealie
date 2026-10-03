import errno
import logging
import socket
import sys
from typing import Any

import uvicorn
from uvicorn.config import STARTUP_FAILURE, Config
from uvicorn.server import Server
from uvicorn.supervisors import Multiprocess

# Uvicorn imports this string in each worker. The development reloader in mealie.app is separate.
_ASGI_APP = "mealie.app:app"
_BACKLOG = 2048
# EADDRNOTAVAIL is how a disabled IPv6 stack reports that the "::" wildcard cannot be assigned,
# after has_dualstack_ipv6() has already returned true. It is not an address-in-use or permission error.
_IPV6_UNAVAILABLE = frozenset(
    code
    for code in (
        errno.EAFNOSUPPORT,
        errno.EPROTONOSUPPORT,
        getattr(errno, "EPFNOSUPPORT", None),
        errno.EADDRNOTAVAIL,
    )
    if isinstance(code, int)
)

logger = logging.getLogger(__name__)


def _dualstack_ipv6_supported() -> bool:
    probe = getattr(socket, "has_dualstack_ipv6", None)
    if not callable(probe):
        return False
    try:
        return bool(probe())
    except OSError:
        return False


def _bind_wildcard(address: tuple[str, int], *, family: int, dualstack_ipv6: bool = False) -> socket.socket:
    listener = socket.create_server(address, family=family, backlog=_BACKLOG, dualstack_ipv6=dualstack_ipv6)
    try:
        listener.set_inheritable(True)
    except OSError:
        listener.close()
        raise
    return listener


def create_wildcard_listener(port: int) -> socket.socket:
    """Listen on every interface for ``port``.

    Prefers one ``socket.create_server`` IPv6 wildcard with ``dualstack_ipv6=True`` so a single
    socket accepts IPv4 and IPv6. Falls back to an IPv4 wildcard only when that dual-stack socket
    is unavailable. An address already in use, or a permission error, is raised unchanged and is
    not followed by a second bind.
    """
    if not _dualstack_ipv6_supported():
        return _bind_wildcard(("0.0.0.0", port), family=socket.AF_INET)

    try:
        return _bind_wildcard(("::", port), family=socket.AF_INET6, dualstack_ipv6=True)
    except ValueError as exc:
        if "dualstack_ipv6 not supported" not in str(exc):
            raise
        reason: BaseException = exc
    except OSError as exc:
        if exc.errno not in _IPV6_UNAVAILABLE:
            raise
        reason = exc

    logger.warning("IPv6 dual-stack listen is unavailable (%s); listening on IPv4 only", reason)
    try:
        return _bind_wildcard(("0.0.0.0", port), family=socket.AF_INET)
    except OSError as exc:
        raise exc from reason


def _close_sockets(sockets: list[socket.socket]) -> None:
    for listener in sockets:
        try:
            listener.close()
        except OSError:
            pass


def _serve_sockets(config: Config, sockets: list[socket.socket]) -> None:
    """Run Uvicorn on caller-owned sockets and close those sockets when the call returns."""
    server: Server | None = None
    try:
        server = Server(config=config)
        # Same socket for every worker. Uvicorn's own empty-host bind is IPv4-only for the
        # multiprocess supervisor, and "::" does not guarantee IPv4 on the single-worker path.
        if config.workers > 1:
            Multiprocess(config, sockets=sockets).run()
        else:
            server.run(sockets=sockets)
    except KeyboardInterrupt:
        pass
    finally:
        _close_sockets(sockets)

    if server is not None and config.workers == 1 and not server.started:
        sys.exit(STARTUP_FAILURE)


def _run_automatic(app: str, port: int, **options: Any) -> None:
    listener = create_wildcard_listener(port)
    try:
        config = Config(app, host="", port=port, **options)
    except BaseException:
        listener.close()
        raise
    _serve_sockets(config, [listener])


def _run_server(app: str, *, host: str, port: int, **options: Any) -> None:
    if host:
        uvicorn.run(app, host=host, port=port, **options)
        return
    _run_automatic(app, port, **options)


def _load_settings() -> tuple[Any, Any]:
    """Load cached settings after the application import has configured logging."""
    from mealie.app import settings as imported_settings
    from mealie.core.config import get_app_settings
    from mealie.core.logger.config import log_config

    settings = get_app_settings()
    # Referencing the import-time instance keeps mealie.app loaded before workers spawn.
    _ = imported_settings.API_PORT
    return settings, log_config()


def main() -> None:
    settings, log_configuration = _load_settings()
    options = {
        "log_level": settings.LOG_LEVEL.lower(),
        "log_config": log_configuration,
        "workers": settings.WORKERS,
        "forwarded_allow_ips": settings.HOST_IP,
        "ssl_keyfile": settings.TLS_PRIVATE_KEY_PATH,
        "ssl_certfile": settings.TLS_CERTIFICATE_PATH,
        "ws": "websockets-sansio",
    }
    _run_server(_ASGI_APP, host=settings.API_HOST, port=settings.API_PORT, **options)


if __name__ == "__main__":
    main()
