"""
Regression tests for SPAStaticFiles.get_response status code behaviour.

Prior to the fix, StaticFiles(html=True) served 404.html (the SPA shell) with
status_code=404, which caused reverse proxies that intercept 4xx to replace the
Mealie UI with a generic error page on every client-side route refresh.

See: https://github.com/mealie-recipes/mealie/issues/7512
"""

import pytest

from mealie.routes.spa import SPAStaticFiles

# Minimal ASGI scope for StaticFiles.get_response.
# StaticFiles checks scope["method"] for 405 guard and passes scope to
# Headers() (which reads scope["headers"]) and URL() (which reads scope["path"]).
_SCOPE = {
    "type": "http",
    "method": "GET",
    "path": "/test",
    "headers": [],
}


@pytest.fixture()
def spa_dir(tmp_path):
    """Temporary directory with the two HTML files the SPA build produces."""
    (tmp_path / "index.html").write_text("<!DOCTYPE html><html><head></head><body>index</body></html>")
    (tmp_path / "404.html").write_text("<!DOCTYPE html><html><head></head><body>spa-shell</body></html>")
    return tmp_path


@pytest.mark.asyncio
async def test_unknown_path_returns_200_with_html_body(spa_dir):
    """Unknown SPA routes must return 200, not 404.

    This is the regression test for #7512: StaticFiles(html=True) serves
    404.html with status 404; SPAStaticFiles must rewrite that to 200.
    """
    spa = SPAStaticFiles(directory=str(spa_dir), html=True)
    response = await spa.get_response("nonexistent-route", _SCOPE)

    assert response.status_code == 200
    assert response.media_type == "text/html"


@pytest.mark.asyncio
async def test_known_path_returns_200(spa_dir):
    """Directly requested index.html must also return 200."""
    spa = SPAStaticFiles(directory=str(spa_dir), html=True)
    response = await spa.get_response("index.html", _SCOPE)

    assert response.status_code == 200
    assert response.media_type == "text/html"


@pytest.mark.asyncio
async def test_without_404_html_falls_back_to_index(tmp_path):
    """When 404.html is absent, the except-branch safety net serves index.html.

    This verifies that the dead-code fallback (catch HTTPException(404), serve
    index.html) still works when 404.html is not present in the build output.
    The status rewrite does NOT fire in this path because super().get_response
    raises rather than returns a 404 response.
    """
    (tmp_path / "index.html").write_text("<!DOCTYPE html><html><head></head><body>index</body></html>")
    # Deliberately omit 404.html so Starlette raises HTTPException(404)

    spa = SPAStaticFiles(directory=str(tmp_path), html=True)
    response = await spa.get_response("nonexistent-route", _SCOPE)

    assert response.status_code == 200
    assert response.media_type == "text/html"
