from pathlib import Path

from fastapi.testclient import TestClient

from mealie.core.config import app_dirs
from tests.app_routes import AppRoutes


def test_update_user_image(
    api_client: TestClient, api_routes: AppRoutes, test_image_jpg: Path, test_image_png: Path, admin_token
):
    response = api_client.post(
        api_routes.users_id_image(2), files={"profile_image": test_image_jpg.open("rb")}, headers=admin_token
    )

    assert response.status_code == 200

    response = api_client.post(
        api_routes.users_id_image(2), files={"profile_image": test_image_png.open("rb")}, headers=admin_token
    )

    assert response.status_code == 200

    directory = app_dirs.USER_DIR.joinpath("2")
    assert directory.joinpath("profile_image.png").is_file()

    # Old profile images are removed
    assert 1 == len([file for file in directory.glob("profile_image.*") if file.is_file()])
