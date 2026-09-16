import contextlib
import os
from collections.abc import Generator
from pathlib import Path

import pytest
from pytest import MonkeyPatch, fixture

# Under pytest-xdist, each worker (gw0, gw1, ...) imports this module in its own
# process. Give each worker its own data dir so they don't fight over the same
# SQLite file / uploads / temp files. Unset when not running under xdist, which
# keeps today's single shared tests/.temp behavior for a plain `pytest` run.
_WORKER_ID = os.environ.get("PYTEST_XDIST_WORKER", "")
_TEMP_DIR = Path(__file__).parent / (f".temp/{_WORKER_ID}" if _WORKER_ID else ".temp")


def _clean_temp_dir():
    with contextlib.suppress(Exception):
        if _TEMP_DIR.exists():
            import shutil

            shutil.rmtree(_TEMP_DIR, ignore_errors=True)


_clean_temp_dir()

mp = MonkeyPatch()
mp.setenv("PRODUCTION", "True")
mp.setenv("TESTING", "True")
mp.setenv("ALLOW_SIGNUP", "True")
if _WORKER_ID:
    mp.setenv("DATA_DIR", f"tests/.temp/{_WORKER_ID}")

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


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """
    Requires --dist loadgroup (see Taskfile py:test). Many test modules share
    mutable state via module-scoped fixtures/globals, and rely on their tests
    running together, in order, on one xdist worker. Default every test to a
    group keyed by its file, so that's true unless a test explicitly opts out
    with its own @pytest.mark.xdist_group (e.g. verified-independent tests
    that can be scheduled freely across workers for better parallelism).
    """
    for item in items:
        if not item.get_closest_marker("xdist_group"):
            item.add_marker(pytest.mark.xdist_group(name=str(item.fspath)))
