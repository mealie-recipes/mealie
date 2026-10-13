import asyncio
from collections.abc import Generator
from typing import Any

import httpx
import pytest
from django.core.handlers.asgi import ASGIHandler
from pydantic import BaseModel

from mealie.app import app
from mealie.core.config import get_app_settings
from mealie.http.api import APIRoute, BackgroundTasks, Depends, File, Form, Query
from mealie.http.responses import BackgroundTask, EventSourceResponse, FileResponse, ServerSentEvent, UploadFile

PATH = "/api/app/about"


@pytest.fixture
async def asgi_client():
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        yield client


def temporary_route(monkeypatch: pytest.MonkeyPatch, endpoint: Any, method: str = "GET", **kwargs: Any) -> None:
    # Reuse an existing Django URL pattern while testing an isolated DRF contract.
    monkeypatch.setattr(app, "routes", [APIRoute(PATH, endpoint, {method}, endpoint.__name__, **kwargs)])


def test_default_application_is_django():
    assert isinstance(app.application, ASGIHandler)
    import sys

    assert not any(name == "fastapi" or name.startswith("fastapi.") for name in sys.modules)


@pytest.mark.asyncio
async def test_asgi_authentication_and_tenant_identity(unique_user):
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/users/self", headers=unique_user.token)
        assert response.status_code == 200
        assert response.json()["id"] == str(unique_user.user_id)
        assert response.json()["groupId"] == str(unique_user.repos.group_id)
        rejected = await client.get("/api/users/self", headers={"Authorization": "Bearer invalid"})
        assert rejected.status_code == 401
        assert rejected.headers["www-authenticate"] == "Bearer"


@pytest.mark.asyncio
async def test_asgi_sse_dependencies_and_background_tasks(monkeypatch):
    events: list[str] = []

    def resource() -> Generator[list[str]]:
        events.append("open")
        try:
            yield events
        finally:
            events.append("close")

    async def endpoint(bg: BackgroundTasks, state: list[str] = Depends(resource)):
        assert state == ["open"]
        yield ServerSentEvent(event="progress", data={"message": "working"})
        await asyncio.sleep(0)
        bg.add_task(events.append, "background")
        assert "close" not in state
        yield ServerSentEvent(event="done", data={"slug": "recipe"})

    temporary_route(monkeypatch, endpoint, response_class=EventSourceResponse)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get(PATH)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream"
    assert 'event: done\ndata: {"slug":"recipe"}\n\n' in response.text
    assert events == ["open", "background", "close"]


@pytest.mark.asyncio
async def test_asgi_upload_aliases_and_repeated_query_values(monkeypatch):
    async def endpoint(
        file: UploadFile = File(...),
        extension: str = Form(...),
        enabled: bool = Form(False, alias="createNewOrganizers"),
        tags: list[str] = Query(...),
    ):
        return {"data": (await file.read()).decode(), "extension": extension, "enabled": enabled, "tags": tags}

    temporary_route(monkeypatch, endpoint, "POST")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            PATH + "?tags=one&tags=two",
            files={"file": ("data.txt", b"payload", "text/plain")},
            data={"extension": "txt", "createNewOrganizers": "true"},
        )
    assert response.status_code == 200
    assert response.json() == {"data": "payload", "extension": "txt", "enabled": True, "tags": ["one", "two"]}


class Payload(BaseModel):
    count: int


@pytest.mark.asyncio
@pytest.mark.parametrize("body", [b'{"count":"invalid"}', b'{"count":', b"{}"])
async def test_asgi_production_validation_envelope(monkeypatch, body):
    settings = get_app_settings()
    monkeypatch.setattr(settings, "TESTING", False)
    monkeypatch.setattr(settings, "PRODUCTION", True)

    def endpoint(data: Payload):
        return data

    temporary_route(monkeypatch, endpoint, "POST")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(PATH, content=body, headers={"Content-Type": "application/json"})
    assert response.status_code == 422
    assert set(response.json()) == {"detail"}
    assert response.json()["detail"][0]["loc"][0] == "body"


@pytest.mark.asyncio
async def test_asgi_download_range_and_cleanup(monkeypatch, tmp_path):
    file = tmp_path / "download.txt"
    file.write_bytes(b"0123456789")
    cleaned: list[bool] = []

    def endpoint():
        return FileResponse(file, filename="download.txt", background=BackgroundTask(cleaned.append, True))

    temporary_route(monkeypatch, endpoint)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get(PATH, headers={"Range": "bytes=2-5"})
    assert response.status_code == 206
    assert response.content == b"2345"
    assert response.headers["content-range"] == "bytes 2-5/10"
    assert "attachment" in response.headers["content-disposition"]
    assert cleaned == [True]


@pytest.mark.asyncio
async def test_scheduler_shutdown_owns_later_tasks():
    from mealie.services.scheduler.runner import scheduler_tasks, track_task
    from mealie.services.scheduler.scheduler_service import SchedulerService

    task = asyncio.create_task(asyncio.sleep(60))
    track_task(task)
    await SchedulerService.stop()
    assert task.cancelled()
    assert not scheduler_tasks


@pytest.mark.asyncio
async def test_raw_json_headers_and_method_contract(monkeypatch):
    from mealie.routes._base.routers import MealieCrudRoute
    from mealie.routes.recipe._base import JSONBytes

    def endpoint():
        return JSONBytes(b'{"updatedAt":"2026-10-01T00:00:00Z"}')

    temporary_route(monkeypatch, endpoint, route_class=MealieCrudRoute)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get(PATH)
        rejected = await client.post(PATH)
    assert response.headers["last-modified"] == "2026-10-01T00:00:00Z"
    assert response.headers["cache-control"] == "no-cache, no-store, must-revalidate"
    assert "allow" not in response.headers
    assert rejected.status_code == 405
    assert rejected.headers["allow"] == "GET"


@pytest.mark.asyncio
async def test_form_contract_does_not_accept_json_credentials(monkeypatch):
    def endpoint(username: str = Form("")):
        return {"username": username}

    temporary_route(monkeypatch, endpoint, "POST")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(PATH, json={"username": "user"})
    assert response.json() == {"username": ""}


@pytest.mark.asyncio
async def test_multipart_part_limit_is_preserved(monkeypatch):
    def endpoint(content: str = Form(...)):
        return {"length": len(content)}

    temporary_route(monkeypatch, endpoint, "POST")
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(PATH, files={"content": (None, "x" * (1024 * 1024 + 1))})
    assert response.status_code == 400
    assert response.json()["detail"] == "Part exceeded maximum size of 1024KB."


@pytest.mark.asyncio
async def test_multi_range_download(monkeypatch, tmp_path):
    file = tmp_path / "ranges.txt"
    file.write_bytes(b"0123456789")

    def endpoint():
        return FileResponse(file)

    temporary_route(monkeypatch, endpoint)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get(PATH, headers={"Range": "bytes=0-2,7-9", "Accept-Encoding": "identity"})
    assert response.status_code == 206
    assert response.headers["content-type"].startswith("multipart/byteranges; boundary=")
    assert b"Content-Range: bytes 0-2/10\n\n012\n" in response.content
    assert b"Content-Range: bytes 7-9/10\n\n789\n" in response.content
    assert int(response.headers["content-length"]) == len(response.content)


@pytest.mark.asyncio
async def test_default_asgi_lifecycle_initializes_and_stops(monkeypatch):
    import mealie.db.init_db as init_db
    import mealie.http.lifecycle as lifecycle

    events = []
    monkeypatch.setattr(init_db, "main", lambda: events.append("database"))

    async def start():
        events.append("scheduler")

    async def stop():
        events.append("stop")

    monkeypatch.setattr(lifecycle, "start_scheduler", start)
    monkeypatch.setattr(lifecycle.SchedulerService, "stop", stop)
    messages = iter([{"type": "lifespan.startup"}, {"type": "lifespan.shutdown"}])

    async def receive():
        return next(messages)

    async def send(message):
        events.append(message["type"])

    await app({"type": "lifespan"}, receive, send)
    assert events == ["database", "scheduler", "lifespan.startup.complete", "stop", "lifespan.shutdown.complete"]
