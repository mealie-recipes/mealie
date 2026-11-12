import errno
import ipaddress
import logging
import socket
import sys

import uvicorn
from uvicorn.config import STARTUP_FAILURE

from mealie.app import settings
from mealie.core.logger.config import log_config

# EADDRNOTAVAIL is how a disabled IPv6 stack reports that the "::" wildcard cannot be assigned,
# after has_dualstack_ipv6() has already returned true. It is not an address-in-use or permission error.
_IPV6_UNAVAILABLE = frozenset(
    code
    for code in (errno.EAFNOSUPPORT, errno.EPROTONOSUPPORT, getattr(errno, "EPFNOSUPPORT", None), errno.EADDRNOTAVAIL)
    if isinstance(code, int)
)

logger = logging.getLogger(__name__)


def create_wildcard_listener(port: int) -> socket.socket:
    """Listen on every interface for ``port``: one dual-stack IPv6 socket, else IPv4 ``0.0.0.0``.

    An address already in use, or a permission error, is raised unchanged and is not followed
    by a second bind.
    """
    if socket.has_dualstack_ipv6():
        try:
            return socket.create_server(("::", port), family=socket.AF_INET6, dualstack_ipv6=True, backlog=2048)
        except OSError as exc:
            if exc.errno not in _IPV6_UNAVAILABLE:
                raise
            logger.warning("IPv6 dual-stack listen is unavailable (%s); listening on IPv4 only", exc)
    return socket.create_server(("0.0.0.0", port), backlog=2048)


def _with_mapped_proxy_ips(allow_ips: str) -> str:
    """Also trust the IPv4-mapped form of each IPv4 proxy, which is how IPv4 peers reach a dual-stack socket."""
    extras: list[str] = []
    for token in (part.strip() for part in allow_ips.split(",")):
        try:
            parsed = ipaddress.ip_network(token) if "/" in token else ipaddress.ip_address(token)
        except ValueError:
            continue
        if isinstance(parsed, ipaddress.IPv4Network):
            extras.append(f"{parsed.network_address.ipv6_mapped}/{96 + parsed.prefixlen}")
        elif isinstance(parsed, ipaddress.IPv4Address):
            extras.append(str(parsed.ipv6_mapped))
    return f"{allow_ips},{','.join(extras)}" if extras else allow_ips


def main():
    options = {
        "log_level": settings.LOG_LEVEL.lower(),
        "log_config": log_config(),
        "workers": settings.WORKERS,
        "forwarded_allow_ips": settings.HOST_IP,
        "ssl_keyfile": settings.TLS_PRIVATE_KEY_PATH,
        "ssl_certfile": settings.TLS_CERTIFICATE_PATH,
        "ws": "websockets-sansio",
    }
    if settings.API_HOST:
        uvicorn.run("mealie.app:app", host=settings.API_HOST, port=settings.API_PORT, **options)
        return

    # Passing host="::" to uvicorn is not enough: with one worker it binds through asyncio's
    # create_server, which sets IPV6_V6ONLY, so IPv4 clients are refused. Bind the dual-stack
    # socket here and hand uvicorn its file descriptor, which every worker count accepts.
    try:
        listener = create_wildcard_listener(settings.API_PORT)
    except OSError as exc:
        # Match uvicorn's own bind failure: log the error and exit with STARTUP_FAILURE, no traceback.
        logger.error(exc)
        sys.exit(STARTUP_FAILURE)
    with listener:
        if listener.family == socket.AF_INET6:
            options["forwarded_allow_ips"] = _with_mapped_proxy_ips(settings.HOST_IP)
        uvicorn.run("mealie.app:app", fd=listener.fileno(), **options)


if __name__ == "__main__":
    main()
