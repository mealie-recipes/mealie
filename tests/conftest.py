import json

import requests
from fastapi.testclient import TestClient
from mealie.app import app
from mealie.core.config import SQLITE_DIR
from mealie.db.database import db
from mealie.db.db_setup import generate_session, sql_global_init
from mealie.db.init_db import init_db
from mealie.routes.deps import get_current_user
from mealie.schema.user import UserInDB
from pytest import fixture
from sqlalchemy.orm.session import Session

from tests.test_config import TEST_DATA

SQLITE_FILE = SQLITE_DIR.joinpath("test.db")
SQLITE_FILE.unlink(missing_ok=True)
TOKEN_URL = "/api/auth/token"


TestSessionLocal = sql_global_init(SQLITE_FILE, check_thread=False)
init_db(TestSessionLocal())


def override_get_db():
    try:
        db = TestSessionLocal()
        yield db
    finally:
        db.close()


@fixture(scope="session")
def api_client():

    app.dependency_overrides[generate_session] = override_get_db

    yield TestClient(app)

    SQLITE_FILE.unlink()


@fixture(scope="session")
def test_image():
    return TEST_DATA.joinpath("test_image.jpg")


@fixture(scope="session")
def token(api_client: requests):
    form_data = {"username": "changeme@email.com", "password": "MyPassword"}
    response = api_client.post(TOKEN_URL, form_data)

    token = json.loads(response.text).get("access_token")

    return {"Authorization": f"Bearer {token}"}
