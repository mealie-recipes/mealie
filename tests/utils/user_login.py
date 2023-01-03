import json

from fastapi.testclient import TestClient

from tests.utils import api_routes


def login(form_data, api_client: TestClient):
    response = api_client.post(api_routes.auth_token, data=form_data)
    assert response.status_code == 200
    token = json.loads(response.text).get("access_token")
    return {"Authorization": f"Bearer {token}"}
