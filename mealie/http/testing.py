"""HTTPX-style integration client executing the Django/DRF WSGI stack."""

import sys
from contextvars import ContextVar
from typing import Any

import httpx
from asgiref.sync import async_to_sync
from django.core.signals import got_request_exception
from django.core.wsgi import get_wsgi_application

_exceptions: ContextVar[list[Any] | None] = ContextVar("http_test_exceptions", default=None)


def capture_exception(sender: Any, **kwargs: Any) -> None:
    if (errors := _exceptions.get()) is not None:
        errors.append(sys.exc_info())


got_request_exception.connect(capture_exception, weak=False)


class TestClient(httpx.Client):
    __test__ = False

    def __init__(self, app: Any = None, **kwargs: Any) -> None:
        application = get_wsgi_application()
        raise_exceptions = kwargs.pop("raise_server_exceptions", True)

        def wsgi(environ: Any, start_response: Any) -> Any:
            errors: list[Any] = []
            token = _exceptions.set(errors)
            try:
                response = application(environ, start_response)
            finally:
                _exceptions.reset(token)
            if errors and raise_exceptions:
                response.close()
                _, exception, traceback = errors[0]
                raise exception.with_traceback(traceback)
            # Django exposes async SSE generators for ASGI. Consume them in one
            # event loop for WSGI tests, keeping their dependencies open throughout.
            if getattr(response, "is_async", False):

                async def consume() -> list[bytes]:
                    return [chunk async for chunk in response.streaming_content]

                try:
                    return iter(async_to_sync(consume)())
                finally:
                    response.close()
            return response

        super().__init__(
            transport=httpx.WSGITransport(app=wsgi, raise_app_exceptions=raise_exceptions),
            base_url=kwargs.pop("base_url", "http://testserver"),
            follow_redirects=True,
            **kwargs,
        )
