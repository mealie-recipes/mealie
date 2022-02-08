from dataclasses import dataclass

import pytest
from fastapi.testclient import TestClient

from tests import utils
from tests.fixtures.fixture_users import build_unique_user
from tests.utils.factories import random_string


@dataclass
class MultiTenant:
    user_one: utils.TestUser
    user_two: utils.TestUser


@pytest.fixture(scope="module")
def multitenants(api_client: TestClient) -> MultiTenant:
    yield MultiTenant(
        user_one=build_unique_user(random_string(12), api_client),
        user_two=build_unique_user(random_string(12), api_client),
    )
