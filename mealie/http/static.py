from pathlib import Path
from typing import Any

from django.http import HttpResponse
from django.utils.http import parse_http_date_safe

from mealie.http.api import HTTPException
from mealie.http.responses import FileResponse, RedirectResponse


class SPAStaticFiles:
    """Nuxt's generated SPA shell and safe static asset serving through Django."""

    def __init__(self, directory: str, html: bool = True) -> None:
        self.directory = Path(directory).resolve()
        self.html = html

    async def get_response(self, path: str, scope: dict[str, Any]) -> Any:
        if scope.get("method", "GET") not in ("GET", "HEAD"):
            raise HTTPException(405)
        candidate = (self.directory / path.lstrip("/")).resolve()
        if not candidate.is_relative_to(self.directory):
            raise HTTPException(404)
        if candidate.is_dir() and (candidate / "index.html").is_file():
            if not scope.get("path", "/").endswith("/"):
                location = "/" + scope.get("path", path).lstrip("/") + "/"
                query = scope.get("query_string", b"").decode()
                return RedirectResponse(location + ("?" + query if query else ""))
            candidate /= "index.html"
        if not candidate.is_file():
            candidate = self.directory / ("404.html" if (self.directory / "404.html").exists() else "index.html")
        if not candidate.is_file():
            raise HTTPException(404)
        response = FileResponse(candidate)
        if path.startswith("_nuxt/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        elif response.media_type == "text/html":
            response.headers["Cache-Control"] = "no-cache"
        headers = {key.decode().lower(): value.decode() for key, value in scope.get("headers", [])}
        etags = headers.get("if-none-match", "")
        modified = parse_http_date_safe(headers.get("if-modified-since", ""))
        if response.headers["etag"] in [tag.strip().removeprefix("W/") for tag in etags.split(",")] or (
            not etags and modified is not None and int(candidate.stat().st_mtime) <= modified
        ):
            response.close()
            return HttpResponse(
                status=304,
                headers={
                    k: v
                    for k, v in response.headers.items()
                    if k.lower()
                    in {
                        "etag",
                        "cache-control",
                        "last-modified",
                    }
                },
            )
        return response
