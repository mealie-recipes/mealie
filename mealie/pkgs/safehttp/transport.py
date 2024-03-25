import ipaddress
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


def resolve_ip_with_socket(domain_name: str):
    """
    Resolve the IP address of a given URL. If the URL is invalid,
    return None.
    """
    try:
        ip_address = socket.gethostbyname(domain_name)
        return ip_address
    except (socket.gaierror, ValueError):
        return None


__disallow_list = [
    "0.0.0.0/32",  # Current network (only valid as source address)
    "10.0.0.0/8",  # Used for local communications within a private network
    # Shared address space for communications between a service provider and its subscribers
    # when using a carrier-grade NAT.
    "100.64.0.0/10",
    "127.0.0.0/8",  # Used for loopback addresses to the local host
    # Used for link-local addresses between two hosts on a single link when no IP address is otherwise specified
    "169.254.0.0/16",
    "172.16.0.0/12",  # Used for local communications within a private network
    "192.0.0.0/24",  # IETF Protocol Assignments
    "192.0.2.0/24",  # Assigned as TEST-NET-1, documentation and examples
    "192.0.2.0/24",  # Assigned as TEST-NET-1, documentation and examples
    "192.168.0.0/16",  # Used for local communications within a private network
    "192.88.99.0/24",  # Reserved. Formerly used for IPv6 to IPv4 relay (included IPv6 address block 2002::/16)
    "198.18.0.0/15",  # Used for benchmark testing of inter-network communications between two separate subnets
    "198.51.100.0/24",  # Assigned as TEST-NET-2, documentation and examples
    "203.0.113.0/24",  # Assigned as TEST-NET-3
    "224.0.0.0/4",  # In use for IP multicast.[9] (Former Class D network)
    "240.0.0.0/4",  # Reserved for future use
    "255.255.255.255/32",  # Reserved for the "limited broadcast" destination address
]


def is_local_ip(ip_address):
    for local_ip in __disallow_list:
        if ip_address in ipaddress.ip_network(local_ip):
            return True
    return False


class AsyncSafeTransport(httpx.AsyncBaseTransport):
    """
    A wrapper around the httpx transport class that enforces a timeout value
    and that the request is not made to a local IP address.
    """

    timeout: int = 15

    def __init__(self, **kwargs):
        self.timeout = kwargs.pop("timeout", self.timeout)
        self._wrapper = httpx.AsyncHTTPTransport(**kwargs)

    async def handle_async_request(self, request):
        # override timeout value for _all_ requests
        request.extensions["timeout"] = httpx.Timeout(self.timeout, pool=self.timeout).as_dict()

        # validate the request is not attempting to connect to a local IP
        # This is a security measure to prevent SSRF attacks

        ip_address = resolve_ip_with_socket(str(request.url.netloc))

        if ip_address and is_local_ip(ip_address):
            raise InvalidDomainError(f"invalid request on local resource: {request.url} -> {ip_address}")

        return await self._wrapper.handle_async_request(request)

    async def aclose(self):
        await self._wrapper.aclose()
