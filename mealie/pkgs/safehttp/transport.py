import ipaddress
import logging
import socket
from collections.abc import Sequence
from typing import Any

import httpx
from curl_cffi import CurlOpt
from httpx_curl_cffi import AsyncCurlTransport, CurlTransport

IPAddress = ipaddress.IPv4Address | ipaddress.IPv6Address
IPNetwork = ipaddress.IPv4Network | ipaddress.IPv6Network

# Carrier-grade NAT. `is_private` does not cover this range on every Python
# version, so we check it explicitly.
CGNAT_NETWORK = ipaddress.ip_network("100.64.0.0/10")


class ForcedTimeoutException(Exception):
    """
    Raised when a request takes longer than the timeout value.
    """

    ...


class InvalidDomainError(Exception):
    """
    Raised when a request targets a disallowed (e.g. local/internal) address.
    """

    ...


def _normalize(ip: IPAddress) -> IPAddress:
    # Unwrap IPv4-mapped IPv6 (e.g. ::ffff:127.0.0.1) so a mapped address can't
    # dodge the IPv4 checks below.
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
        return ip.ipv4_mapped
    return ip


def is_blocked_ip(ip: IPAddress) -> bool:
    """Return True if connecting to this address should never be allowed by default."""
    ip = _normalize(ip)
    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True
    return isinstance(ip, ipaddress.IPv4Address) and ip in CGNAT_NETWORK


def _parse_host_list(entries: Sequence[str]) -> tuple[set[str], list[IPNetwork]]:
    """Split configured entries into exact hostnames and IP networks (CIDRs)."""
    hosts: set[str] = set()
    networks: list[IPNetwork] = []
    for entry in entries:
        cleaned = entry.strip().lower()
        if not cleaned:
            continue
        try:
            networks.append(ipaddress.ip_network(cleaned, strict=False))
        except ValueError:
            hosts.add(cleaned)
    return hosts, networks


def _matches(host: str, ips: Sequence[IPAddress], hosts: set[str], networks: list[IPNetwork]) -> bool:
    if host.lower() in hosts:
        return True
    for ip in ips:
        normalized = _normalize(ip)
        for network in networks:
            if normalized.version == network.version and normalized in network:
                return True
    return False


class _SafeTransportMixin:
    """
    Shared SSRF protection for the sync and async curl transports.

    On each request it resolves the host once, validates every resolved address,
    and pins the connection to the validated address(es) via curl's RESOLVE option
    so curl cannot re-resolve to a different (e.g. rebound) IP.

    Not safe for concurrent requests on a single transport instance: the pin is
    applied through the shared session. Mealie uses a fresh transport per scrape
    and per outbound POST, and redirects are followed sequentially.
    """

    timeout: int = 15
    # set by the curl transport base class this mixin is combined with
    _session: Any

    def __init__(
        self,
        *,
        log: logging.Logger | None = None,
        allow_hosts: Sequence[str] = (),
        deny_hosts: Sequence[str] = (),
        timeout: int | None = None,
        **kwargs,
    ) -> None:
        self._log = log
        self._allow = _parse_host_list(allow_hosts)
        self._deny = _parse_host_list(deny_hosts)
        if timeout is not None:
            self.timeout = timeout
        super().__init__(**kwargs)

    def _validate(self, request: httpx.Request) -> list[str] | None:
        """Validate the request target. Returns the curl RESOLVE pins, or None for an IP literal."""
        # Force our timeout onto every request.
        request.extensions["timeout"] = httpx.Timeout(self.timeout, pool=self.timeout).as_dict()

        host = request.url.host
        port = request.url.port or (443 if request.url.scheme == "https" else 80)

        try:
            literal: IPAddress | None = ipaddress.ip_address(host)
        except ValueError:
            literal = None

        if literal is not None:
            ips: list[IPAddress] = [literal]
        else:
            try:
                infos = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
            except (socket.gaierror, UnicodeError) as e:
                # An unencodable hostname (e.g. an over-long label) raises UnicodeError, not
                # gaierror. Either way the host is unusable, so it fails as an invalid domain.
                raise InvalidDomainError(f"could not resolve host: {host}") from e

            ips = []
            seen: set[str] = set()
            for info in infos:
                addr = str(info[4][0]).split("%")[0]  # drop any IPv6 scope id
                if addr not in seen:
                    seen.add(addr)
                    ips.append(ipaddress.ip_address(addr))

        deny_hosts, deny_networks = self._deny
        if _matches(host, ips, deny_hosts, deny_networks):
            self._warn(request, "target is on the disallow list")
            raise InvalidDomainError(f"request blocked by disallow list: {request.url}")

        allow_hosts, allow_networks = self._allow
        if not _matches(host, ips, allow_hosts, allow_networks):
            for ip in ips:
                if is_blocked_ip(ip):
                    self._warn(request, f"resolves to non-public address {ip}")
                    raise InvalidDomainError(f"invalid request on local resource: {request.url} -> {ip}")

        if literal is not None:
            # curl connects straight to the literal address; nothing to pin.
            return None
        return [f"{host}:{port}:{ip}" for ip in ips]

    def _warn(self, request: httpx.Request, reason: str) -> None:
        if self._log:
            self._log.warning(f"[safehttp] blocked request to {request.url}: {reason}")

    def _apply_pin(self, resolve: list[str] | None) -> None:
        # curl_cffi applies the session's curl_options to each request, so setting
        # RESOLVE here pins this request to the address we just validated.
        options = self._session.curl_options
        if resolve:
            options[CurlOpt.RESOLVE] = resolve
        else:
            options.pop(CurlOpt.RESOLVE, None)


class AsyncSafeTransport(_SafeTransportMixin, AsyncCurlTransport):
    """Async curl transport that blocks SSRF and pins the connection to a validated IP."""

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        resolve = self._validate(request)
        self._apply_pin(resolve)
        return await super().handle_async_request(request)


class SafeTransport(_SafeTransportMixin, CurlTransport):
    """Sync counterpart of AsyncSafeTransport for server-initiated POSTs (webhooks, recipe actions)."""

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        resolve = self._validate(request)
        self._apply_pin(resolve)
        return super().handle_request(request)


def post(
    url: str,
    *,
    json=None,
    timeout: int = 15,
    allow_hosts: Sequence[str] = (),
    deny_hosts: Sequence[str] = (),
    **kwargs,
) -> httpx.Response:
    """Perform a sync POST through the SSRF-protected transport.

    Drop-in for `requests.post(url, json=..., timeout=...)` on server-initiated
    requests to user-supplied URLs. Redirects are followed and re-validated per hop.
    """
    transport = SafeTransport(allow_hosts=allow_hosts, deny_hosts=deny_hosts, timeout=timeout)
    with httpx.Client(transport=transport, follow_redirects=True) as client:
        return client.post(url, json=json, timeout=timeout, **kwargs)
