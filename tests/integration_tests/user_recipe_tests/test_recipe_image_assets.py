import filecmp

from fastapi.testclient import TestClient
from slugify import slugify

from mealie.schema.recipe.recipe import Recipe
from tests import data
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_recipe_assets_create(api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe):
    recipe = recipe_ingredient_only
    payload = {
        "slug": recipe.slug,
        "name": random_string(10),
        "icon": random_string(10),
        "extension": "jpg",
    }

    file_payload = {
        "file": data.images_test_image_1.read_bytes(),
    }

    response = api_client.post(
        f"/api/recipes/{recipe.slug}/assets",
        data=payload,
        files=file_payload,
        headers=unique_user.token,
    )
    assert response.status_code == 200

    # Ensure asset was created
    asset_path = recipe.asset_dir / str(slugify(payload["name"]) + "." + payload["extension"])

    assert asset_path.exists()
    assert filecmp.cmp(asset_path, data.images_test_image_1)

    # Ensure asset data is included in recipe
    response = api_client.get(f"/api/recipes/{recipe.slug}", headers=unique_user.token)
    recipe_respons = response.json()

    assert recipe_respons["assets"][0]["name"] == payload["name"]


def test_recipe_image_upload(api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe):
    data_payload = {"extension": "jpg"}
    file_payload = {"image": data.images_test_image_1.read_bytes()}

    response = api_client.put(
        f"/api/recipes/{recipe_ingredient_only.slug}/image",
        data=data_payload,
        files=file_payload,
        headers=unique_user.token,
    )

    assert response.status_code == 200

    image_version = response.json()["image"]

    # Get Recipe check for version
    response = api_client.get(f"/api/recipes/{recipe_ingredient_only.slug}", headers=unique_user.token)
    recipe_respons = response.json()
    assert recipe_respons["image"] == image_version
