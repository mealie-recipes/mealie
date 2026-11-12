from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse
from starlette.status import HTTP_413_CONTENT_TOO_LARGE
from starlette.types import ASGIApp, Message, Receive, Scope, Send


class BodyTooLargeError(HTTPException):
    def __init__(self) -> None:
        super().__init__(status_code=HTTP_413_CONTENT_TOO_LARGE, detail="Request body is too large")


class BodySizeLimitMiddleware:
    """
    Rejects requests whose body is larger than `max_body_size` bytes with a 413.

    FastAPI reads the body before it resolves dependencies, auth included, so without this an
    anonymous client can stream an unbounded upload to disk before getting its 401. The declared
    Content-Length is checked up front, and the bytes actually received are counted as well, since
    a chunked request declares no length.
    """

    def __init__(self, app: ASGIApp, max_body_size: int) -> None:
        self.app = app
        self.max_body_size = max_body_size

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        for name, value in scope["headers"]:
            if name == b"content-length" and value.isdigit() and int(value) > self.max_body_size:
                await self._reject(scope, receive, send)
                return

        received = 0
        response_started = False

        async def limited_receive() -> Message:
            nonlocal received
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_body_size:
                    raise BodyTooLargeError()
            return message

        async def tracking_send(message: Message) -> None:
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
            await send(message)

        try:
            await self.app(scope, limited_receive, tracking_send)
        except BodyTooLargeError:
            # Routes that read the body themselves, rather than through FastAPI's parsing, let the
            # error escape the app's exception handlers.
            if response_started:
                raise
            await self._reject(scope, receive, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send) -> None:
        response = JSONResponse({"detail": "Request body is too large"}, status_code=HTTP_413_CONTENT_TOO_LARGE)
        await response(scope, receive, send)
