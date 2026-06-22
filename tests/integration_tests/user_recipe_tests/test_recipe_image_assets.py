import filecmp

import pytest
from fastapi.testclient import TestClient
from httpx import Response
from slugify import slugify

from mealie.pkgs.safehttp.transport import AsyncSafeTransport
from mealie.schema.recipe.recipe import Recipe
from tests import data
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_recipe_assets_create(api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe):
    recipe = recipe_ingredient_only
    payload = {
        "name": random_string(10),
        "icon": random_string(10),
        "extension": "jpg",
    }

    file_payload = {
        "file": data.images_test_image_1.read_bytes(),
    }

    response = api_client.post(
        f"/api/recipes/{recipe.slug}/assets",
        data=payload,
        files=file_payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # Ensure asset was created
    asset_path = recipe.asset_dir / str(slugify(payload["name"]) + "." + payload["extension"])

    assert asset_path.exists()
    assert filecmp.cmp(asset_path, data.images_test_image_1)

    # Ensure asset data is included in recipe
    response = api_client.get(f"/api/recipes/{recipe.slug}", headers=unique_user.token)
    recipe_respons = response.json()

    assert recipe_respons["assets"][0]["name"] == payload["name"]


def test_recipe_asset_exploit(api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe):
    """
    Test to ensure that users are unable to circumvent the destination directory when uploading a file
    as an asset to the recipe. This was reported via huntr and was confirmed to be a severe security issue.

    A mitigation is implemented by ensuring that the destination file is checked to ensure that the parent directory
    is the recipe's asset directory. Otherwise, an exception is raised and a 400 error is returned.

    Report Details:
    -------------------
    Arbitrary template creation leading to Authenticated Remote Code Execution in hay-kot/mealie

    An attacker who is able to execute such a flaw is able to execute commands with the privileges
    of the programming language or the web server. In this case, since the attacker is root in a
    Docker container they can execute system commands, read/modify databases, attack adjacent
    systems. This flaw leads to a complete compromise of the system.

    https://huntr.dev/bounties/3ecd4a78-523e-4f84-a3fd-31a01a68f142/
    """

    recipe = recipe_ingredient_only
    payload = {
        "name": "$",
        "icon": random_string(10),
        "extension": "./test.txt",
    }

    file_payload = {
        "file": data.images_test_image_1.read_bytes(),
    }

    response = api_client.post(
        f"/api/recipes/{recipe.slug}/assets",
        data=payload,
        files=file_payload,
        headers=unique_user.token,
    )

    assert response.status_code == 400

    # Ensure File was not created
    assert not (recipe.asset_dir.parent / "test.txt").exists()
    assert not (recipe.asset_dir / "test.txt").exists()


def test_recipe_asset_dangerous_extension_blocked(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe
):
    """Ensure scriptable extensions are rejected to prevent stored XSS (GHSA-gfwc-pjx4-mg9p)."""
    recipe = recipe_ingredient_only
    for ext in ("html", "svg", "js", "htm", "xhtml"):
        payload = {"name": random_string(10), "icon": "mdi-file", "extension": ext}
        file_payload = {"file": b"<script>alert(1)</script>"}
        response = api_client.post(
            f"/api/recipes/{recipe.slug}/assets",
            data=payload,
            files=file_payload,
            headers=unique_user.token,
        )
        assert response.status_code == 400, f"expected 400 for extension={ext}, got {response.status_code}"


def test_recipe_asset_served_as_attachment(
    api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe
):
    """Assets must be served as downloads with MIME sniffing disabled so uploaded files cannot
    execute as active content in Mealie's origin."""
    recipe = recipe_ingredient_only
    payload = {"name": random_string(10), "icon": "mdi-file", "extension": "txt"}
    file_payload = {"file": b"<script>alert(1)</script>"}

    response = api_client.post(
        f"/api/recipes/{recipe.slug}/assets",
        data=payload,
        files=file_payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    recipe_response = api_client.get(f"/api/recipes/{recipe.slug}", headers=unique_user.token).json()
    recipe_id = recipe_response["id"]
    file_name = recipe_response["assets"][0]["fileName"]

    media_response = api_client.get(f"/api/media/recipes/{recipe_id}/assets/{file_name}")
    assert media_response.status_code == 200
    assert "attachment" in media_response.headers["content-disposition"].lower()
    assert media_response.headers["x-content-type-options"] == "nosniff"


def test_recipe_image_upload(api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe):
    data_payload = {"extension": "jpg"}
    file_payload = {"image": data.images_test_image_1.read_bytes()}

    response = api_client.put(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        data=data_payload,
        files=file_payload,
        headers=unique_user.token,
    )

    assert response.status_code == 200

    image_version = response.json()["image"]

    # Get Recipe check for version
    response = api_client.get(f"/api/recipes/{recipe_ingredient_only.slug}", headers=unique_user.token)
    recipe_respons = response.json()
    assert recipe_respons["image"] == image_version


# Regression tests for https://github.com/mealie-recipes/mealie/issues/7578
# `POST /api/recipes/{slug}/image` (the URL scrape path) used to silently
# return 200 OK when the upstream image fetch failed, leaving the recipe
# with no image and the caller none the wiser. It must now surface 502
# Bad Gateway with the upstream status code in the body.


@pytest.mark.parametrize("upstream_status", [403, 404, 460, 500, 502, 503])
def test_scrape_image_url_returns_502_on_upstream_non_2xx(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_ingredient_only: Recipe,
    monkeypatch: pytest.MonkeyPatch,
    upstream_status: int,
):
    """Upstream returning a non-2xx (e.g. 460 from a WAF-fronted CDN) must
    surface as 502 Bad Gateway with the upstream status in the body, not
    as the old silently-correct 200 OK."""

    async def return_non_2xx(*args, **kwargs):
        return Response(upstream_status, content=b"")

    monkeypatch.setattr(AsyncSafeTransport, "handle_async_request", return_non_2xx)

    response = api_client.post(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        json={"url": "https://example.com/waf-blocked.jpg"},
        headers=unique_user.token,
    )

    assert response.status_code == 502
    body = response.json()
    # The upstream status code should be surfaced in the error detail so
    # callers can distinguish a 460 WAF block from a 500 server error.
    assert str(upstream_status) in str(body)


def test_scrape_image_url_returns_502_on_transport_error(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_ingredient_only: Recipe,
    monkeypatch: pytest.MonkeyPatch,
):
    """Network-level failures (DNS, TLS, timeout) must also surface as
    502 Bad Gateway rather than the old silent 200 OK."""

    async def raise_connection_error(*args, **kwargs):
        raise ConnectionError("simulated network failure")

    monkeypatch.setattr(AsyncSafeTransport, "handle_async_request", raise_connection_error)

    response = api_client.post(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        json={"url": "https://example.com/timeout.jpg"},
        headers=unique_user.token,
    )

    assert response.status_code == 502


def test_scrape_image_service_raises_on_non_2xx():
    """Direct unit test on RecipeDataService.scrape_image — the data
    service must raise ImageFetchError rather than swallowing the failure
    and returning None as it did before #7578."""

    import asyncio
    from unittest.mock import MagicMock
    from uuid import uuid4

    from mealie.services.recipe.recipe_data_service import (
        ImageFetchError,
        RecipeDataService,
    )

    # Use a plain MagicMock for the logger so calls to .info / .exception
    # are no-ops (the service code calls both, including the exception path).
    service = RecipeDataService(recipe_id=uuid4(), logger=MagicMock())

    async def run():
        # Build a fake httpx AsyncClient context manager
        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def get(self, *args, **kwargs):
                return Response(460, content=b"")

        # Patch AsyncClient via the module under test so the data service
        # uses our fake client instead of opening a real network connection.
        import mealie.services.recipe.recipe_data_service as mod

        original_async_client = mod.AsyncClient
        mod.AsyncClient = lambda *a, **kw: FakeClient()
        try:
            await service.scrape_image("https://example.com/waf.jpg")
        except ImageFetchError as e:
            assert e.status_code == 460
            return "raised"
        finally:
            mod.AsyncClient = original_async_client
        return "no-raise"

    assert asyncio.run(run()) == "raised"


# Regression tests for https://github.com/mealie-recipes/mealie/issues/7489
# Some recipe sites serve real image bytes with a `Content-Type:
# application/octet-stream` header (or no content-type at all), because
# their CDN / object store is configured to skip MIME sniffing. The
# previous strict `if "image" not in content_type: raise NotAnImageError`
# logic rejected those, killing the recipe image even though the bytes
# decoded fine as a JPEG. The fix: when the content-type is missing or
# not `image/*`, defer to Pillow to verify the bytes are actually a
# decodable image. Real non-image bodies (HTML, JSON, ...) still fail,
# but via Pillow's `UnidentifiedImageError` rather than via the header.


def test_scrape_image_url_accepts_octet_stream_with_real_jpeg_bytes(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_ingredient_only: Recipe,
    monkeypatch: pytest.MonkeyPatch,
):
    """`Content-Type: application/octet-stream` + a real JPEG body must
    succeed. This is the grubby.co.uk / DigitalOcean Spaces case in #7489."""

    jpeg_bytes = data.images_test_image_1.read_bytes()

    async def return_octet_stream_jpeg(*args, **kwargs):
        return Response(200, headers={"content-type": "application/octet-stream"}, content=jpeg_bytes)

    monkeypatch.setattr(AsyncSafeTransport, "handle_async_request", return_octet_stream_jpeg)

    response = api_client.post(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        json={"url": "https://grubby.co.uk/recipe/photo.jpg"},
        headers=unique_user.token,
    )

    assert response.status_code == 200, response.text


def test_scrape_image_url_accepts_missing_content_type_with_real_jpeg_bytes(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_ingredient_only: Recipe,
    monkeypatch: pytest.MonkeyPatch,
):
    """Some servers omit the content-type header entirely; same fix path
    as octet-stream — Pillow verifies the bytes are a real image."""

    jpeg_bytes = data.images_test_image_1.read_bytes()

    async def return_no_ct_jpeg(*args, **kwargs):
        return Response(200, headers={}, content=jpeg_bytes)

    monkeypatch.setattr(AsyncSafeTransport, "handle_async_request", return_no_ct_jpeg)

    response = api_client.post(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        json={"url": "https://example.com/no-ct.jpg"},
        headers=unique_user.token,
    )

    assert response.status_code == 200, response.text


def test_scrape_image_url_rejects_octet_stream_with_non_image_bytes(
    api_client: TestClient,
    unique_user: TestUser,
    recipe_ingredient_only: Recipe,
    monkeypatch: pytest.MonkeyPatch,
):
    """`application/octet-stream` must NOT be a magic "accept anything"
    pass. A real non-image body (HTML, here) must still fail — surfaced
    as a 500 carrying the NotAnImageError message. The previous behavior
    also raised, but with a different message and on the header alone."""

    async def return_octet_stream_html(*args, **kwargs):
        return Response(
            200,
            headers={"content-type": "application/octet-stream"},
            content=b"<html><body>not an image</body></html>",
        )

    monkeypatch.setattr(AsyncSafeTransport, "handle_async_request", return_octet_stream_html)

    response = api_client.post(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        json={"url": "https://example.com/wrong-bytes.jpg"},
        headers=unique_user.token,
    )

    # Non-image bytes must still fail. The route doesn't translate
    # NotAnImageError specifically, so we get a 500 — what matters for
    # the regression is that the recipe did NOT get a 200 / image written.
    assert response.status_code != 200
    # The recipe should still have no image (write_image was never called).
    recipe_resp = api_client.get(f"/api/recipes/{recipe_ingredient_only.slug}", headers=unique_user.token).json()
    assert not recipe_resp.get("image")


def test_scrape_image_service_accepts_octet_stream_jpeg_bytes():
    """Direct unit test on RecipeDataService.scrape_image: an octet-stream
    response carrying real JPEG bytes must succeed, and must NOT raise
    NotAnImageError. Without the #7489 fix this raises because the
    header doesn't contain the substring 'image'."""

    import asyncio
    from unittest.mock import MagicMock
    from uuid import uuid4

    from mealie.services.recipe.recipe_data_service import (
        NotAnImageError,
        RecipeDataService,
    )

    service = RecipeDataService(recipe_id=uuid4(), logger=MagicMock())
    jpeg_bytes = data.images_test_image_1.read_bytes()

    async def run():
        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def get(self, *args, **kwargs):
                return Response(
                    200,
                    headers={"content-type": "application/octet-stream"},
                    content=jpeg_bytes,
                )

        import mealie.services.recipe.recipe_data_service as mod

        original_async_client = mod.AsyncClient
        mod.AsyncClient = lambda *a, **kw: FakeClient()
        try:
            await service.scrape_image("https://grubby.co.uk/recipe/photo.jpg")
            return "ok"
        except NotAnImageError:
            return "raised-NotAnImageError"
        finally:
            mod.AsyncClient = original_async_client

    assert asyncio.run(run()) == "ok"


def test_scrape_image_service_rejects_octet_stream_html_bytes():
    """Counterpart: octet-stream + non-image bytes must still raise
    NotAnImageError (now via Pillow, not the header check)."""

    import asyncio
    from unittest.mock import MagicMock
    from uuid import uuid4

    from mealie.services.recipe.recipe_data_service import (
        NotAnImageError,
        RecipeDataService,
    )

    service = RecipeDataService(recipe_id=uuid4(), logger=MagicMock())

    async def run():
        class FakeClient:
            async def __aenter__(self):
                return self

            async def __aexit__(self, *args):
                return False

            async def get(self, *args, **kwargs):
                return Response(
                    200,
                    headers={"content-type": "application/octet-stream"},
                    content=b"<html>not an image</html>",
                )

        import mealie.services.recipe.recipe_data_service as mod

        original_async_client = mod.AsyncClient
        mod.AsyncClient = lambda *a, **kw: FakeClient()
        try:
            await service.scrape_image("https://example.com/wrong.jpg")
            return "no-raise"
        except NotAnImageError:
            return "raised-NotAnImageError"
        finally:
            mod.AsyncClient = original_async_client

    assert asyncio.run(run()) == "raised-NotAnImageError"
