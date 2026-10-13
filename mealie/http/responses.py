import asyncio
import inspect
import json
import mimetypes
from collections.abc import Callable
from http.cookies import Morsel
from pathlib import Path
from typing import Any, BinaryIO
from urllib.parse import quote

from asgiref.sync import async_to_sync
from django.http import FileResponse as DjangoFileResponse
from django.http import HttpResponse, StreamingHttpResponse
from django.utils.http import http_date
from pydantic import BaseModel, model_validator

from mealie.http.encoding import jsonable_encoder


class BackgroundTask:
    def __init__(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.func, self.args, self.kwargs = func, args, kwargs

    def run(self) -> None:
        if inspect.iscoroutinefunction(self.func):
            async_to_sync(self.func)(*self.args, **self.kwargs)
        else:
            self.func(*self.args, **self.kwargs)


class BackgroundTasks:
    def __init__(self) -> None:
        self.tasks: list[BackgroundTask] = []

    def add_task(self, func: Callable, *args: Any, **kwargs: Any) -> None:
        self.tasks.append(BackgroundTask(func, *args, **kwargs))

    def run(self) -> None:
        for task in self.tasks:
            task.run()

    async def run_async(self) -> None:
        for task in self.tasks:
            if inspect.iscoroutinefunction(task.func):
                await task.func(*task.args, **task.kwargs)
            else:
                await asyncio.to_thread(task.func, *task.args, **task.kwargs)


class Response(HttpResponse):
    def __init__(
        self,
        content: Any = b"",
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        self.media_type = media_type
        super().__init__(self.render_content(content), status=status_code, headers=headers, content_type=media_type)
        if media_type is None:
            self.headers.pop("Content-Type", None)
        if background:
            self._resource_closers.append(background.run)

    def render_content(self, content: Any) -> bytes:
        if content is None:
            return b""
        return content if isinstance(content, bytes) else str(content).encode("utf-8")

    @property
    def body(self) -> bytes:
        return self.content

    @property
    def raw_headers(self) -> list[tuple[bytes, bytes]]:
        return [(k.lower().encode(), v.encode()) for k, v in self.headers.items()] + [
            (b"set-cookie", morsel.OutputString().encode()) for morsel in self.cookies.values()
        ]

    def set_cookie(self, key: str, value: str = "", *, partitioned: bool = False, **kwargs: Any) -> None:
        expires = kwargs.get("expires")
        if isinstance(expires, int):
            kwargs["expires"] = http_date(expires)
        super().set_cookie(key, value, **kwargs)
        if expires is None:
            self.cookies[key]["expires"] = ""
        if partitioned:
            self.cookies[key]["partitioned"] = True
        morsel = self.cookies[key]
        compatible = CookieMorsel()
        compatible.set(morsel.key, morsel.value, morsel.coded_value)
        compatible.update(morsel)
        self.cookies[key] = compatible


class CookieMorsel(Morsel):
    def output(self, attrs: Any = None, header: str = "Set-Cookie:") -> str:
        return super().output(attrs, header).lstrip()


class JSONResponse(Response):
    media_type = "application/json"

    def __init__(self, content: Any, **kwargs: Any) -> None:
        super().__init__(content, media_type=self.media_type, **kwargs)

    def render_content(self, content: Any) -> bytes:
        return json.dumps(
            jsonable_encoder(content), ensure_ascii=False, allow_nan=False, separators=(",", ":")
        ).encode()


class RedirectResponse(Response):
    def __init__(self, url: str, status_code: int = 307, **kwargs: Any) -> None:
        super().__init__(status_code=status_code, **kwargs)
        self.headers["location"] = quote(str(url), safe=":/%#?=@[]!$&'()*+,;")


class FileResponse(DjangoFileResponse):
    def __init__(
        self,
        path: str | Path,
        *,
        status_code: int = 200,
        media_type: str | None = None,
        filename: str | None = None,
        background: BackgroundTask | None = None,
        headers: dict[str, str] | None = None,
        content_disposition_type: str = "attachment",
    ) -> None:
        self.path = Path(path)
        self.media_type = media_type or mimetypes.guess_type(str(path))[0] or "text/plain"
        super().__init__(
            LazyFile(self.path),
            status=status_code,
            content_type=self.media_type,
            as_attachment=bool(filename) and content_disposition_type == "attachment",
            filename=filename or "",
            headers=headers,
        )
        stat = self.path.stat()
        if self.media_type.startswith("text/"):
            self.headers["content-type"] = self.media_type + "; charset=utf-8"
        if filename is None:
            self.headers.pop("content-disposition", None)
        self.headers["last-modified"] = http_date(stat.st_mtime)
        import hashlib

        self.headers["etag"] = (
            '"' + hashlib.md5(f"{stat.st_mtime}-{stat.st_size}".encode(), usedforsecurity=False).hexdigest() + '"'
        )
        self.headers["accept-ranges"] = "bytes"
        if background:
            self._resource_closers.append(background.run)


class LazyFile:
    """Django can describe a file without opening it until streaming starts."""

    def __init__(self, path: Path) -> None:
        self.name = str(path)
        self._file: BinaryIO | None = None

    def open(self) -> BinaryIO:
        if self._file is None:
            self._file = open(self.name, "rb")
        return self._file

    def read(self, size: int = -1) -> bytes:
        return self.open().read(size)

    def seek(self, offset: int, whence: int = 0) -> int:
        return self.open().seek(offset, whence)

    def tell(self) -> int:
        return self._file.tell() if self._file else 0

    def seekable(self) -> bool:
        return False

    def close(self) -> None:
        if self._file:
            self._file.close()


class UploadFile:
    def __init__(
        self, file: BinaryIO, filename: str | None = None, headers: Any = None, size: int | None = None
    ) -> None:
        self.file = file
        self.filename = filename
        self.headers = headers or {}
        self.size = size
        self.content_type = self.headers.get("content-type")

    async def read(self, size: int = -1) -> bytes:
        return self.file.read(size)

    async def seek(self, offset: int) -> None:
        self.file.seek(offset)

    async def close(self) -> None:
        self.file.close()


class ServerSentEvent(BaseModel):
    data: Any = None
    raw_data: str | None = None
    event: str | None = None
    id: str | None = None
    retry: int | None = None
    comment: str | None = None

    @model_validator(mode="after")
    def validate_event(self) -> ServerSentEvent:
        if self.data is not None and self.raw_data is not None:
            raise ValueError("Cannot set both data and raw_data")
        for value in (self.event, self.id):
            if value is not None and ("\r" in value or "\n" in value):
                raise ValueError("SSE event and id must be single lines")
        if self.id is not None and "\0" in self.id:
            raise ValueError("SSE id must not contain null characters")
        if self.retry is not None and self.retry < 0:
            raise ValueError("SSE retry must be non-negative")
        return self

    def encode(self) -> bytes:
        lines: list[str] = []
        if self.comment is not None:
            lines.extend(": " + line for line in self.comment.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
        for key in ("event", "id", "retry"):
            value = getattr(self, key)
            if value is not None:
                lines.append(f"{key}: {value}")
        if self.raw_data is not None or self.data is not None:
            data = (
                self.raw_data
                if self.raw_data is not None
                else json.dumps(jsonable_encoder(self.data), ensure_ascii=False, separators=(",", ":"))
            )
            lines.extend("data: " + line for line in data.replace("\r\n", "\n").replace("\r", "\n").split("\n"))
        return ("\n".join(lines) + "\n\n").encode()


class EventSourceResponse(StreamingHttpResponse):
    media_type = "text/event-stream"

    def __init__(self, content: Any, status_code: int = 200, **kwargs: Any) -> None:
        async def encode() -> Any:
            try:
                async for event in content:
                    yield (event if isinstance(event, ServerSentEvent) else ServerSentEvent(data=event)).encode()
            finally:
                if hasattr(content, "aclose"):
                    await content.aclose()

        super().__init__(encode(), status=status_code, content_type=self.media_type, **kwargs)
        self.headers["cache-control"] = "no-cache"
        self.headers["x-accel-buffering"] = "no"


def copy_headers(source: HttpResponse, target: HttpResponse) -> None:
    for key, value in source.headers.items():
        target.headers[key] = value
    target.cookies.update(source.cookies)
    if source.status_code != 200:
        target.status_code = source.status_code
