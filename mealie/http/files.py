import re
import secrets
from collections.abc import Iterator
from typing import Any

from mealie.http.responses import FileResponse


def parse_ranges(header: str, size: int) -> list[tuple[int, int]]:
    unit, separator, values = header.partition("=")
    if not separator or unit.strip() != "bytes":
        raise ValueError("Only support bytes range")
    result = []
    for value in values.split(","):
        match = re.fullmatch(r"\s*(\d*)-(\d*)\s*", value)
        if not match or not any(match.groups()):
            raise ValueError("Malformed range header.")
        first, last = match.groups()
        start = int(first) if first else max(0, size - int(last))
        end = min(int(last), size - 1) if first and last else size - 1
        if start >= size or start > end:
            raise IndexError("Range not satisfiable")
        result.append((start, end))
    merged: list[tuple[int, int]] = []
    for start, end in sorted(result):
        if merged and start <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(end, merged[-1][1]))
        else:
            merged.append((start, end))
    return merged


def prepare_file_response(response: FileResponse, request: Any) -> None:
    """Byte ranges and incremental ASGI file delivery without buffering the file."""
    size = response.path.stat().st_size
    ranges = [(0, size - 1)]
    header = request.headers.get("range")
    boundary = None
    prefixes: list[bytes] = []
    if header and request.headers.get("if-range", response.headers["etag"]) in (
        response.headers["etag"],
        response.headers["last-modified"],
    ):
        try:
            ranges = parse_ranges(header, size)
        except (ValueError, IndexError) as exc:
            response.status_code = 416 if isinstance(exc, IndexError) else 400
            if isinstance(exc, IndexError):
                response.headers["content-range"] = f"*/{size}"
            response.streaming_content = [str(exc).encode()]
            response.headers["content-length"] = str(len(str(exc).encode()))
            return
        response.status_code = 206
        if len(ranges) == 1:
            start, end = ranges[0]
            response.headers["content-range"] = f"bytes {start}-{end}/{size}"
            response.headers["content-length"] = str(end - start + 1)
        else:
            boundary = secrets.token_hex(13)
            media_type = response.headers["content-type"]
            response.headers["content-type"] = f"multipart/byteranges; boundary={boundary}"
            prefixes = [
                f"--{boundary}\nContent-Type: {media_type}\nContent-Range: bytes {start}-{end}/{size}\n\n".encode()
                for start, end in ranges
            ]
            response.headers["content-length"] = str(
                sum(len(prefix) + end - start + 2 for prefix, (start, end) in zip(prefixes, ranges, strict=True))
                + len(f"\n--{boundary}--\n".encode())
            )
    handle = response.file_to_stream

    def chunks() -> Iterator[bytes]:
        for index, (start, end) in enumerate(ranges):
            if boundary:
                yield prefixes[index]
            handle.seek(start)
            remaining = end - start + 1
            while remaining > 0:
                chunk = handle.read(min(65536, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
            if boundary:
                yield b"\n"
        if boundary:
            yield f"\n--{boundary}--\n".encode()

    async def async_chunks() -> Any:
        import asyncio

        iterator = chunks()
        sentinel = object()
        while (chunk := await asyncio.to_thread(next, iterator, sentinel)) is not sentinel:
            yield chunk

    response.streaming_content = async_chunks() if hasattr(request, "scope") else chunks()
