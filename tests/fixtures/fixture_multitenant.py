from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from tests import utils
from tests.fixtures.fixture_users import build_unique_user
from tests.utils.factories import random_string


@dataclass
class MultiTenant:
    user_one: utils.TestUser
    user_two: utils.TestUser


@pytest.fixture(scope="module")
def multitenants(session: Session, api_client: TestClient) -> MultiTenant:
    yield MultiTenant(
        user_one=build_unique_user(session, random_string(12), api_client),
        user_two=build_unique_user(session, random_string(12), api_client),
    )
