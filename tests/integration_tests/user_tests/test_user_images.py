from fastapi.testclient import TestClient

from tests import data as test_data
from tests.utils.fixture_schemas import TestUser


class Routes:
    def get_user_image(user_id: str, file_name: str = "profile.webp") -> str:
        return f"/api/media/users/{user_id}/{file_name}"

    def user_image(user_id: str) -> str:
        return f"/api/users/{user_id}/image"


def test_user_get_image(api_client: TestClient, unique_user: TestUser):
    # Get the user's image
    response = api_client.get(Routes.get_user_image(str(unique_user.user_id)))
    assert response.status_code == 200

    # Ensure that the returned value is a valid image
    assert response.headers["Content-Type"] == "image/webp"


def test_user_update_image(api_client: TestClient, unique_user: TestUser):
    image = {"profile": test_data.images_test_image_1.read_bytes()}

    # Update the user's image
    response = api_client.post(Routes.user_image(str(unique_user.user_id)), files=image, headers=unique_user.token)
    assert response.status_code == 200

    # Request the image again
    response = api_client.get(Routes.get_user_image(str(unique_user.user_id)))
    assert response.status_code == 200
