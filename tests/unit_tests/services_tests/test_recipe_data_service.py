import uuid
from pathlib import Path

import httpx
import pytest

from mealie.pkgs import safehttp
from mealie.schema.recipe.recipe import Recipe
from mealie.services.recipe import recipe_data_service
from mealie.services.recipe.recipe_data_service import (
    InvalidDomainError,
    NotAnImageError,
    RecipeDataService,
)


@pytest.fixture
def data_service(tmp_path: Path, monkeypatch) -> RecipeDataService:
    """A service rooted in a temp dir, so nothing touches the real recipe data directory."""
    recipe_id = uuid.uuid4()
    monkeypatch.setattr(Recipe, "directory_from_id", classmethod(lambda cls, rid: tmp_path.joinpath(str(rid))))
    return RecipeDataService(recipe_id)


@pytest.fixture
def written(monkeypatch) -> list[tuple[bytes, str]]:
    """Records what gets handed to the writer, without dragging Pillow into the test."""
    calls: list[tuple[bytes, str]] = []

    def fake_write_image(self, file_data, extension, image_dir=None):
        calls.append((file_data, extension))
        return Path("original.webp")

    monkeypatch.setattr(RecipeDataService, "write_image", fake_write_image)
    return calls


def _response(content_type: str | None, content: bytes = b"image-bytes") -> safehttp.FetchResult:
    """A successful fetch. `content_type` of None omits the header entirely."""
    return safehttp.FetchResult(
        content=content,
        status_code=200,
        url="https://example.test/photo",
        headers=httpx.Headers({} if content_type is None else {"content-type": content_type}),
        encoding=None,
    )


def _patch_fetch(monkeypatch, result=None, *, raises: Exception | None = None) -> dict:
    """Replaces the network call, capturing the url and options it was given."""
    captured: dict = {}

    async def fake_fetch(url, **kwargs):
        captured["url"] = url
        captured["kwargs"] = kwargs
        if raises is not None:
            raise raises
        return result

    monkeypatch.setattr(safehttp, "resilient_fetch", fake_fetch)
    return captured


# ---------------------------------------------------------------------------
# fetch_image
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_fetch_image_takes_extension_from_content_type(data_service, monkeypatch):
    """The URL is often extensionless or query-laden, so the response decides the extension."""
    _patch_fetch(monkeypatch, _response("image/png"))

    downloaded = await data_service.fetch_image("https://example.test/photo?size=large")

    assert downloaded == (b"image-bytes", "png")


@pytest.mark.asyncio
async def test_fetch_image_strips_content_type_parameters(data_service, monkeypatch):
    _patch_fetch(monkeypatch, _response("IMAGE/JPEG; charset=binary"))

    downloaded = await data_service.fetch_image("https://example.test/photo")

    assert downloaded is not None
    assert downloaded[1] == "jpeg"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "content_type",
    [
        "text/html",
        "text/html; name=image.png",  # merely *containing* "image" is not an image
        "application/octet-stream",
        None,  # header absent entirely
    ],
)
async def test_fetch_image_rejects_non_image_content_types(data_service, monkeypatch, content_type):
    _patch_fetch(monkeypatch, _response(content_type))

    with pytest.raises(NotAnImageError):
        await data_service.fetch_image("https://example.test/photo")


@pytest.mark.asyncio
async def test_fetch_image_translates_invalid_domain_error(data_service, monkeypatch):
    """Callers catch this module's error, not the transport's identically-named one."""
    _patch_fetch(monkeypatch, raises=safehttp.InvalidDomainError("blocked"))

    with pytest.raises(InvalidDomainError):
        await data_service.fetch_image("https://169.254.169.254/latest")


@pytest.mark.asyncio
async def test_fetch_image_propagates_too_large(data_service, monkeypatch):
    """Whoever set the budget reports the overrun; it must not flatten into a generic failure."""
    _patch_fetch(monkeypatch, raises=safehttp.ResponseTooLargeError("too big"))

    with pytest.raises(safehttp.ResponseTooLargeError):
        await data_service.fetch_image("https://example.test/photo", max_bytes=10)


@pytest.mark.asyncio
async def test_fetch_image_passes_options_through(data_service, monkeypatch):
    captured = _patch_fetch(monkeypatch, _response("image/png"))

    await data_service.fetch_image("https://example.test/photo", max_bytes=1234)

    assert captured["kwargs"]["max_bytes"] == 1234
    # FlareSolverr returns HTML, so it can never serve an image download.
    assert captured["kwargs"]["allow_flaresolverr"] is False


@pytest.mark.asyncio
async def test_fetch_image_returns_none_when_nothing_downloads(data_service, monkeypatch):
    _patch_fetch(monkeypatch, None)

    assert await data_service.fetch_image("https://example.test/photo") is None


@pytest.mark.asyncio
async def test_fetch_image_swallows_transport_failures(data_service, monkeypatch):
    _patch_fetch(monkeypatch, raises=httpx.ConnectError("boom"))

    assert await data_service.fetch_image("https://example.test/photo") is None


# ---------------------------------------------------------------------------
# scrape_image
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_scrape_image_writes_the_real_extension(data_service, monkeypatch, written):
    """Regression: the old URL-derived guess collapsed to "jpg" for every image."""
    _patch_fetch(monkeypatch, _response("image/png"))

    await data_service.scrape_image("https://example.test/photo")

    assert written == [(b"image-bytes", "png")]


@pytest.mark.asyncio
async def test_scrape_image_is_uncapped(data_service, monkeypatch, written):
    """Recipe images are re-encoded by the minifier, so its output is what bounds them."""
    captured = _patch_fetch(monkeypatch, _response("image/png"))

    await data_service.scrape_image("https://example.test/photo")

    assert captured["kwargs"].get("max_bytes") is None


@pytest.mark.asyncio
async def test_scrape_image_accepts_schema_org_dict(data_service, monkeypatch, written):
    captured = _patch_fetch(monkeypatch, _response("image/webp"))

    await data_service.scrape_image({"url": "https://example.test/photo"})

    assert captured["url"] == "https://example.test/photo"


@pytest.mark.asyncio
async def test_scrape_image_picks_largest_from_a_list(data_service, monkeypatch, written):
    async def fake_largest(urls):
        return urls[-1], 999

    monkeypatch.setattr(recipe_data_service, "largest_content_len", fake_largest)
    captured = _patch_fetch(monkeypatch, _response("image/png"))

    await data_service.scrape_image(["https://example.test/small", "https://example.test/big"])

    assert captured["url"] == "https://example.test/big"


@pytest.mark.asyncio
async def test_scrape_image_rejects_unparseable_input(data_service):
    with pytest.raises(ValueError):
        await data_service.scrape_image({"not-a-url": "x"})


@pytest.mark.asyncio
async def test_scrape_image_returns_none_without_writing_when_download_fails(data_service, monkeypatch, written):
    _patch_fetch(monkeypatch, None)

    assert await data_service.scrape_image("https://example.test/photo") is None
    assert written == []
