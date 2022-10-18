from fastapi.testclient import TestClient

from tests import data as test_data
from tests.utils import api_routes
from tests.utils.fixture_schemas import TestUser


def test_user_get_image(api_client: TestClient, unique_user: TestUser):
    # Get the user's image
    response = api_client.get(api_routes.media_users_user_id_file_name(str(unique_user.user_id), "profile.webp"))
    assert response.status_code == 200

    # Ensure that the returned value is a valid image
    assert response.headers["Content-Type"] == "image/webp"


def test_user_update_image(api_client: TestClient, unique_user: TestUser):
    image = {"profile": test_data.images_test_image_1.read_bytes()}

    # Update the user's image
    response = api_client.post(
        api_routes.users_id_image(str(unique_user.user_id)), files=image, headers=unique_user.token
    )
    assert response.status_code == 200

    # Request the image again
    response = api_client.get(api_routes.media_users_user_id_file_name(str(unique_user.user_id), "profile.webp"))
    assert response.status_code == 200
