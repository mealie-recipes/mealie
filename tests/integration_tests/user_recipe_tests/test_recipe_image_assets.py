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


def test_recipe_asset_exploit(api_client: TestClient, unique_user: TestUser, recipe_ingredient_only: Recipe):
    """
    Test to ensure that users are unable to circumvent the destination directory when uploading a file
    as an asset to the recipe. This was reported via huntr and was confirmed to be a severe security issue.

    A mitigation is implemented by ensuring that the destination file is checked to ensure that the parent directory
    is the recipe's asset directory. Otherwise, an exception is raised and a 400 error is returned.

    Report Details:
    -------------------
    Arbitrary template creation leading to Authenticated Remote Code Execution in hay-kot/mealie

    An attacker who is able to execute such a flaw is able to execute commands with the privileges
    of the programming language or the web server. In this case, since the attacker is root in a
    Docker container they can execute system commands, read/modify databases, attack adjacent
    systems. This flaw leads to a complete compromise of the system.

    https://huntr.dev/bounties/3ecd4a78-523e-4f84-a3fd-31a01a68f142/
    """

    recipe = recipe_ingredient_only
    payload = {
        "name": "$",
        "icon": random_string(10),
        "extension": "./test.txt",
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

    assert response.status_code == 400

    # Ensure File was not created
    assert not (recipe.asset_dir.parent / "test.txt").exists()
    assert not (recipe.asset_dir / "test.txt").exists()


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
