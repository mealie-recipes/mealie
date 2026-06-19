from fastapi.testclient import TestClient

from tests.utils import api_routes


def test_native_config_returns_404_when_oidc_not_configured(api_client: TestClient):
    response = api_client.get(api_routes.auth_oauth_native_config)

    assert response.status_code == 404
    assert response.json()["detail"] == "OIDC is not configured"
