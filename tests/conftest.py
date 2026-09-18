import contextlib
from collections.abc import Generator

from pytest import MonkeyPatch, fixture


def _clean_temp_dir():
    with contextlib.suppress(Exception):
        temp_dir = Path(__file__).parent / ".temp"

        if temp_dir.exists():
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


_clean_temp_dir()

mp = MonkeyPatch()
mp.setenv("PRODUCTION", "True")
mp.setenv("TESTING", "True")
mp.setenv("ALLOW_SIGNUP", "True")
from pathlib import Path

from fastapi.testclient import TestClient

from mealie.app import app
from mealie.core import config
from mealie.db.db_setup import SessionLocal, generate_session
from mealie.db.init_db import main
from tests import data as test_data
from tests.fixtures import *  # noqa: F403 F401

main()


def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@fixture(scope="session")
def api_client():
    app.dependency_overrides[generate_session] = override_get_db

    yield TestClient(app)

    with contextlib.suppress(Exception):
        settings = config.get_app_settings()
        settings.DB_PROVIDER.db_path.unlink()  # Handle SQLite Provider


@fixture(autouse=True)
def isolate_session_cookies(api_client: TestClient):
    """Stops one test's login from authenticating the next test's requests.

    `api_client` is session-scoped, and the server sets a session cookie on every login, so its jar
    accumulates real credentials as the suite runs. Without this, a request that deliberately sends
    no Authorization header is still authenticated by whoever logged in last — which silently turns
    an anonymous-access test into an authenticated one and hides the very thing it was checking.

    Fixtures that log in during setup are higher-scoped, so their cookies are cleared here too. That
    is safe: every fixture hands back an Authorization header, never a cookie.
    """
    api_client.cookies.clear()
    yield
    api_client.cookies.clear()


@fixture(scope="session")
def test_image_jpg():
    return test_data.images_test_image_1


@fixture(scope="session")
def test_image_png():
    return test_data.images_test_image_2


@fixture(scope="session", autouse=True)
def global_cleanup() -> Generator[None, None, None]:
    """Purges the .temp directory used for testing"""

    yield None
    _clean_temp_dir()
