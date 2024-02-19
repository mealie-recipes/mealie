import random
import string

from fastapi.testclient import TestClient

from mealie.core.config import get_app_settings
from tests.utils import api_routes
from tests.utils.factories import user_registration_factory


def test_register_user(api_client: TestClient, monkeypatch):
    # create random registration
    registration = user_registration_factory()

    # signup disabled but valid request
    monkeypatch.setenv("ALLOW_SIGNUP", "False")
    get_app_settings.cache_clear()
    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 403

    # signup disabled, request includes non valid group token
    registration.group_token = "".join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10)).strip()
    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 400

    # signup enabled but contains non valid group token
    monkeypatch.setenv("ALLOW_SIGNUP", "True")
    get_app_settings.cache_clear()
    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 400

    # signup enabled and valid request
    registration.group_token = None
    response = api_client.post(api_routes.users_register, json=registration.model_dump(by_alias=True))
    assert response.status_code == 201
