import json
import zipfile
from io import BytesIO

from fastapi.testclient import TestClient

from tests.utils import api_routes
from tests.utils.factories import random_string
from tests.utils.fixture_schemas import TestUser


def test_zip_import_applies_household_public_preference(
        api_client: TestClient, unique_user: TestUser
) -> None:
    """Recipes imported from a zip should follow the household's recipe_public preference.

    Regression test for https://github.com/mealie-recipes/mealie/issues/7172
    """
    # 1. Make sure the household default is public
    response = api_client.get(api_routes.households_preferences, headers=unique_user.token)
    assert response.status_code == 200
    prefs = response.json()
    prefs["recipePublic"] = True

    response = api_client.put(
        api_routes.households_preferences, json=prefs, headers=unique_user.token
    )
    assert response.status_code == 200

    # 2. Create a recipe, then force its `public` setting to False
    recipe_name = random_string()
    response = api_client.post(api_routes.recipes, json={"name": recipe_name}, headers=unique_user.token)
    assert response.status_code == 201
    slug = response.json()

    recipe = api_client.get(api_routes.recipes_slug(slug), headers=unique_user.token).json()
    recipe["settings"]["public"] = False
    response = api_client.put(api_routes.recipes_slug(slug), json=recipe, headers=unique_user.token)
    assert response.status_code == 200

    # 3. Export it as a zip
    response = api_client.post(
        api_routes.shared_recipes, json={"recipeId": recipe["id"]}, headers=unique_user.token
    )
    assert response.status_code == 201
    token_id = response.json()["id"]

    response = api_client.get(api_routes.recipes_shared_token_id_zip(token_id))
    assert response.status_code == 200
    zip_bytes = BytesIO(response.content)

    # Sanity check: the exported zip really contains a private recipe
    with zipfile.ZipFile(zip_bytes) as zip_fp:
        json_name = next(n for n in zip_fp.namelist() if n.endswith(".json"))
        exported = json.loads(zip_fp.read(json_name))
        assert exported["settings"]["public"] is False

    zip_bytes.seek(0)

    # 4. Import the zip
    response = api_client.post(
        api_routes.recipes_create_zip,
        files={"archive": ("recipe.zip", zip_bytes, "application/zip")},
        headers=unique_user.token,
    )
    assert response.status_code == 201
    imported_slug = response.json()
    assert imported_slug != slug

    # 5. The imported recipe should be public, following the household preference
    imported = api_client.get(api_routes.recipes_slug(imported_slug), headers=unique_user.token).json()
    assert imported["settings"]["public"] is True, (
        "Imported recipe should inherit the household's recipe_public=True preference"
    )