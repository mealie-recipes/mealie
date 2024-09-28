import ipaddress
import logging
import socket

import httpx


class ForcedTimeoutException(Exception):
    """
    Raised when a request takes longer than the timeout value.
    """

    ...


class InvalidDomainError(Exception):
    """
    Raised when a request is made to a local IP address.
    """

    ...


class AsyncSafeTransport(httpx.AsyncBaseTransport):
    """
    A wrapper around the httpx transport class that enforces a timeout value
    and that the request is not made to a local IP address.
    """

    timeout: int = 15

    def __init__(self, log: logging.Logger | None = None, **kwargs):
        self.timeout = kwargs.pop("timeout", self.timeout)
        self._wrapper = httpx.AsyncHTTPTransport(**kwargs)
        self._log = log

    async def handle_async_request(self, request) -> httpx.Response:
        # override timeout value for _all_ requests
        request.extensions["timeout"] = httpx.Timeout(self.timeout, pool=self.timeout).as_dict()

        # validate the request is not attempting to connect to a local IP
        # This is a security measure to prevent SSRF attacks

        ip: ipaddress.IPv4Address | ipaddress.IPv6Address | None = None

        netloc = request.url.netloc.decode()
        if ":" in netloc:  # Either an IP, or a hostname:port combo
            netloc_parts = netloc.split(":")

            netloc = netloc_parts[0]

            try:
                ip = ipaddress.ip_address(netloc)
            except ValueError:
                if self._log:
                    self._log.debug(f"failed to parse ip for {netloc=} falling back to domain resolution")
                pass

        # Request is a domain or a hostname.
        if not ip:
            if self._log:
                self._log.debug(f"resolving IP for domain: {netloc}")

            ip_str = socket.gethostbyname(netloc)
            ip = ipaddress.ip_address(ip_str)

            if self._log:
                self._log.debug(f"resolved IP for domain: {netloc} -> {ip}")

        if ip.is_private:
            if self._log:
                self._log.warning(f"invalid request on local resource: {request.url} -> {ip}")
            raise InvalidDomainError(f"invalid request on local resource: {request.url} -> {ip}")

        return await self._wrapper.handle_async_request(request)

    async def aclose(self):
        await self._wrapper.aclose()
